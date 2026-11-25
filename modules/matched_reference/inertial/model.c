#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#define NV 53
/* Paired vehicle states, 0..19 installed and 20..39 reference.
   40: direct work difference; 41: direct suspension difference;
   42: installed no-contact time; 43: reference no-contact time.
   Classical RK4 step-doubling with event bracketing, continuous Hermite road.
   Units: m, s, N, J. No tyre damping or suspension stops silently introduced. */
typedef struct {const double *r,*dr; int n;double L,v,k,c,h,spacing,offset,amp,travel,ct,stop_k,height,patch,cr,pm;} Model;
static const double a[4]={1.2,1.2,-1.6,-1.6},b[4]={-.8,.8,-.8,.8};
static void input(const Model *m,double t,double *r,double *rd,double *g,double *gd){
 double x=m->v*t,dx=m->L/m->n,u=fmod(x,m->L);if(u<0)u+=m->L;
 double z=u/dx;int j=(int)floor(z),j1=(j+1)%m->n;z-=j;
 double h00=(2*z-3)*z*z+1,h10=((z-2)*z+1)*z,h01=(-2*z+3)*z*z,h11=(z-1)*z*z;
 double d00=(6*z-6)*z,d10=(3*z-4)*z+1,d01=(-6*z+6)*z,d11=(3*z-2)*z;
 for(int i=0;i<4;i++){
  double ra=m->r[4*j+i],rb=m->r[4*j1+i],da=m->dr[4*j+i],db=m->dr[4*j1+i];
  r[i]=m->amp*(h00*ra+h10*dx*da+h01*rb+h11*dx*db);
  rd[i]=m->amp*m->v*(d00*ra/dx+d10*da+d01*rb/dx+d11*db);
  double xx=fmod(x-(i>=2?2.8:0)-m->offset,m->spacing);if(xx<0)xx+=m->spacing;
  // Finite-patch overlap with a 1.1 m translating cover.
  // Reconstructed S profile: h*(3s^2-2s^3), not a digitized measured profile.
  double xx0=xx;if(xx0>m->spacing-m->patch)xx0-=m->spacing;
  double rawlo=xx0-m->patch/2,rawhi=xx0+m->patch/2;
  double lo=fmax(0,rawlo),hi=fmin(1.1,rawhi);
  r[i+4]=rd[i+4]=0;g[i]=gd[i]=0;
  if(hi>lo){
   double dlo=rawlo>0?1:0,dhi=rawhi<1.1?1:0;
   double a=lo/1.1,b=hi/1.1;
   double sa=3*a*a-2*a*a*a,sb=3*b*b-2*b*b*b;
   double ia=a*a*a-.5*a*a*a*a,ib=b*b*b-.5*b*b*b*b;
   g[i]=(hi-lo)/m->patch;gd[i]=m->v*(dhi-dlo)/m->patch;
   r[i+4]=m->height*1.1*(ib-ia)/m->patch;
   rd[i+4]=m->height*m->v*(sb*dhi-sa*dlo)/m->patch;
  }
 }
}

static double travelof(const double*s,int i){return s[0]+a[i]*sin(s[1])+b[i]*cos(s[1])*sin(s[2])-s[3+i];}
static void vehicle(const Model*m,const double*s,const double*r,const double*rd,const double*g,const double*gd,
 int installed,double*d,double*force,double*delta,double*td,double*sd){
 const double sc=2000./1840.,ks=22000*sc,cs=1600*sc,kt=200000*sc;
 memset(d,0,20*sizeof(double));*td=*sd=0;double stat[4];
 for(int i=0;i<4;i++){
  stat[i]=((i<2?1600*9.81*1.6/5.6:1600*9.81*1.2/5.6)+60*9.81)*sc;
  delta[i]=stat[i]/kt+r[i]+(installed?r[i+4]:0)-(installed?g[i]*s[14+i%2]:0)-s[3+i];
 }
 for(int side=0;side<2;side++){
  double A[2],B[2],qd=0;
  for(int j=0;j<2;j++){
   int i=side+2*j;double gg=installed?g[i]:0;
   double rate=rd[i]+(installed?rd[i+4]:0)-(installed?s[14+side]*gd[i]:0)-s[10+i];
   A[j]=kt*fmax(0,delta[i])*(1+m->ct/stat[i]*rate);
   B[j]=kt*fmax(0,delta[i])*m->ct/stat[i]*gg;
  }
  if(installed){
   qd=s[50+side];double Fload=0;
   for(int j=0;j<2;j++){int i=side+2*j;Fload+=g[i]*fmax(0,A[j]-B[j]*qd);}
   double acc=(Fload-m->k*s[14+side]-(qd>=0?m->c:m->cr)*qd)/m->pm;
   if(s[14+side]<=0 && qd<=0 && acc<0){qd=0;acc=0;}
   if(s[14+side]>=m->h && qd>=0 && acc>0){qd=0;acc=0;}
   d[50+side]=acc;
  }
  if(installed)d[14+side]=qd;
  for(int j=0;j<2;j++){
   int i=side+2*j;double gg=installed?g[i]:0;
   double rate=rd[i]+(installed?rd[i+4]:0)-(installed?s[14+side]*gd[i]:0)-gg*qd-s[10+i];
   force[i]=kt*fmax(0,delta[i])*fmax(0,1+m->ct/stat[i]*rate);
   *td+=(force[i]-kt*fmax(0,delta[i]))*rate;
  }
 }
 for(int j=0;j<7;j++)d[j]=s[j+7];
 double mp=sc*(2400*cos(s[2])*cos(s[2])+4200*sin(s[2])*sin(s[2]));
 for(int i=0;i<4;i++){
  double jp=a[i]*cos(s[1])-b[i]*sin(s[1])*sin(s[2]),jr=b[i]*cos(s[1])*cos(s[2]);
  double z=travelof(s,i),zd=s[7]+jp*s[8]+jr*s[9]-s[10+i],sg=z>=0?1:-1;
  double ex=m->travel>0?fmax(0,fabs(z)-m->travel):0,elastic=m->stop_k*ex;
  double stop=elastic*fmax(0,1+2*sg*zd),fs=ks*z+cs*zd+sg*stop;
  *sd+=(stop-elastic)*sg*zd;
  d[7]-=fs/(1600*sc);d[8]-=jp*fs/mp;d[9]-=jr*fs/(1800*sc);
  d[10+i]=(fs+force[i]-stat[i])/(60*sc);
  d[16]+=cs*zd*zd;d[18]+=force[i]*(rd[i]+(installed?rd[i+4]:0));if(installed)d[19]-=force[i]*s[14+i%2]*gd[i];
 }
 double md=3600*sc*sin(s[2])*cos(s[2]);
 d[8]-=md*s[9]*s[8]/mp;d[9]+=.5*md*s[8]*s[8]/(1800*sc);
 if(installed)d[17]=(d[14]>=0?m->c:m->cr)*d[14]*d[14]+(d[15]>=0?m->c:m->cr)*d[15]*d[15];
}

static void rhs(const Model*m,double t,const double*y,double*d){
 double r[8],rd[8],g[4],gd[4],f[4],f0[4],dd[4],td,td0,sd,sd0;input(m,t,r,rd,g,gd);
 vehicle(m,y,r,rd,g,gd,1,d,f,dd,&td,&sd);vehicle(m,y+20,r,rd,g,gd,0,d+20,f0,dd,&td0,&sd0);
 d[40]=d[18]+d[19]-d[38]-d[39];d[41]=d[16]-d[36];d[42]=d[43]=0;
 for(int j=0;j<4;j++){d[42]+=(f[j]<=0)?.25:0;d[43]+=(f0[j]<=0)?.25:0;}
 d[44]=td;d[45]=td0;d[46]=sd;d[47]=sd0;
 d[48]=fmax(0,d[40]);d[49]=fmax(0,-d[40]);d[52]=0;
}
static void rk(const Model*m,double t,const double*y,double h,double*out){
 double k1[NV],k2[NV],k3[NV],k4[NV],z[NV];rhs(m,t,y,k1);
 for(int j=0;j<NV;j++)z[j]=y[j]+h/2*k1[j];rhs(m,t+h/2,z,k2);
 for(int j=0;j<NV;j++)z[j]=y[j]+h/2*k2[j];rhs(m,t+h/2,z,k3);
 for(int j=0;j<NV;j++)z[j]=y[j]+h*k3[j];rhs(m,t+h,z,k4);
 for(int j=0;j<NV;j++)out[j]=y[j]+h/6*(k1[j]+2*k2[j]+2*k3[j]+k4[j]);
}

static void events(const Model*m,double t,const double*y,double*e){
 e[18]=y[14];e[19]=y[15];
 double r[8],rd[8],g[4],gd[4],f[4],de[4],d[NV],td,sd;input(m,t,r,rd,g,gd);
 vehicle(m,y,r,rd,g,gd,1,d,f,de,&td,&sd);for(int j=0;j<4;j++)e[j]=de[j];
 vehicle(m,y+20,r,rd,g,gd,0,d,f,de,&td,&sd);for(int j=0;j<4;j++)e[4+j]=de[j];
 e[8]=m->h-y[14];e[9]=m->h-y[15];
 for(int v=0;v<2;v++)for(int j=0;j<4;j++)e[10+4*v+j]=m->travel>0?m->travel-fabs(travelof(y+20*v,j)):1;
}
static double energy(const Model*m,double t,const double*y,int installed){
 double r[8],rd[8],g[4],gd[4];input(m,t,r,rd,g,gd);
 const double sc=2000./1840.,ks=22000*sc,kt=200000*sc;
 double en=.5*sc*(1600*y[7]*y[7]+(2400*cos(y[2])*cos(y[2])+4200*sin(y[2])*sin(y[2]))*y[8]*y[8]+1800*y[9]*y[9]);
 for(int j=0;j<4;j++){
  double stat=((j<2?1600*9.81*1.6/5.6:1600*9.81*1.2/5.6)+60*9.81)*sc;
  double de=fmax(0,stat/kt+r[j]+(installed?r[j+4]:0)-(installed?g[j]*y[14+j%2]:0)-y[3+j]);
  double z=travelof(y,j);if(m->travel>0){double ex=fmax(0,fabs(z)-m->travel);en+=.5*m->stop_k*ex*ex;}
  en+=.5*(60*sc*y[10+j]*y[10+j]+ks*z*z+kt*de*de)+stat*y[3+j];
 }
 if(installed)en+=.5*m->k*(y[14]*y[14]+y[15]*y[15])+.5*m->pm*(y[50]*y[50]+y[51]*y[51]);return en;
}
int simulate(const double*r,const double*dr,int n,double L,double v,double k,double tau,
 double stroke,double density,double offset,double amp,double warm_m,double run_m,
 double rtol,double maxdt,double travel,double ct,double stop_k,double height,double patch,double return_tau,double plate_mass,const double*initial,double *out){
 Model m={r,dr,n,L,v,k,k*tau,stroke,1000/density,offset,amp,travel,ct,stop_k,height,patch,k*return_tau,plate_mass};
 FILE *tr=NULL;const char *path=getenv("DUARTE_TRACE_PATH");if(path)tr=fopen(path,"w");
 if(tr)fprintf(tr,"x_m,qL_m,qdL_m_s,front_g,rear_g,front_F_N,rear_F_N,plate_F_N,profile_front_m,profile_rear_m\n");
 double y[NV]={0},one[NV],half[NV],two[NV],e0[20],e1[20],tmp[NV],ee[20];
 memcpy(y,initial,NV*sizeof(double));double maxtr=0,maxpitch=0,maxroll=0;int invalid=0;
 double t=-warm_m/v,end=run_m/v,h=fmin(maxdt,.001),en0=0,ref0=0,peak=0,peakf=0;
 long accept=0,reject=0,nev=0;int measured=0;
 while(t<end-1e-11){
  if(!measured && t>=-1e-12){t=0;en0=energy(&m,t,y,1);ref0=energy(&m,t,y+20,0);
   for(int j=16;j<20;j++)y[j]=y[j+20]=0;for(int j=40;j<50;j++)y[j]=0;y[52]=0;measured=1;}
  double boundary=measured?end:0;h=fmin(h,fmin(maxdt,boundary-t));if(h<1e-13)return -2;
  rk(&m,t,y,h,one);events(&m,t,y,e0);events(&m,t+h,one,e1);
  double event_h=h;int hit=-1;
  for(int j=0;j<20;j++){
   int cross=(j<8||j>=10)?(fabs(e0[j])>1e-10 && e0[j]*e1[j]<0):(e0[j]>1e-12 && e1[j]<-1e-12);
   if(!cross)continue;
   double lo=0,hi=h;
   for(int it=0;it<30;it++){
    double mid=.5*(lo+hi);rk(&m,t,y,mid,tmp);events(&m,t+mid,tmp,ee);
    if(e0[j]*ee[j]<=0)hi=mid;else lo=mid;
   }
   if(hi<event_h){event_h=hi;hit=j;}
  }
  if(event_h<h*.999999){h=event_h;rk(&m,t,y,h,one);nev++;}
  rk(&m,t,y,h/2,half);rk(&m,t+h/2,half,h/2,two);
  double err=0;
  for(int block=0;block<2;block++)for(int j=0;j<16;j++){
   int q=20*block+j;double atol=(j<7||j>=14)?1e-9:1e-7;
   double scale=atol+rtol*fmax(fabs(y[q]),fabs(two[q]));
   err=fmax(err,fabs(two[q]-one[q])/(15*scale));
  }
  // Control work increments as well as motions, independently of accumulated totals.
  for(int j=16;j<NV;j++)if(j<20 || j>=36){
   double scale=1e-5+rtol*fabs(two[j]-y[j]);
   err=fmax(err,fabs(two[j]-one[j])/(15*scale));
  }
  if(!isfinite(err))return -3;
  if(err>1 && h>1e-10){h*=fmax(.15,.85*pow(err,-.2));reject++;continue;}
  if(two[14]>stroke+1e-9 || two[15]>stroke+1e-9){h*=.5;reject++;continue;}
  memcpy(y,two,sizeof(y));
  for(int j=14;j<16;j++){
   int qv=50+j-14;
   if(y[j]>=stroke-1e-10 && y[qv]>0){y[52]+=.5*m.pm*y[qv]*y[qv];y[qv]=0;y[j]=stroke;}
   if(y[j]<=1e-10 && y[qv]<0){y[52]+=.5*m.pm*y[qv]*y[qv];y[qv]=0;y[j]=0;}
  }
  t+=h;accept++;
  maxpitch=fmax(maxpitch,fmax(fabs(y[1]),fabs(y[21])));maxroll=fmax(maxroll,fmax(fabs(y[2]),fabs(y[22])));
  if(maxpitch>=M_PI/2 || maxroll>=M_PI/2){invalid=1;break;}
  if(measured){peak=fmax(peak,fmax(y[14],y[15]));double rr[8],rd[8],g[4],gd[4],f[4],de[4],d[NV],td,sd;
   input(&m,t,rr,rd,g,gd);vehicle(&m,y,rr,rd,g,gd,1,d,f,de,&td,&sd);
   if(tr && t*v<18)fprintf(tr,"%.12g,%.12g,%.12g,%.12g,%.12g,%.12g,%.12g,%.12g,%.12g,%.12g\n",t*v,y[14],d[14],g[0],g[2],f[0],f[2],g[0]*f[0]+g[2]*f[2],rr[4],rr[6]);
   for(int j=0;j<4;j++){peakf=fmax(peakf,f[j]);maxtr=fmax(maxtr,fabs(travelof(y,j)));}}
  h*=err<1e-15?2.0:fmin(2.,fmax(.25,.9*pow(err,-.2)));
  if(accept>20000000)return -5;
 }
 double de=energy(&m,t,y,1)-en0,de0=energy(&m,t,y+20,0)-ref0;
 if(tr)fclose(tr);
 out[0]=y[17]+y[52];out[1]=y[40];out[2]=y[41];out[3]=de-de0;
 out[4]=y[18]+y[19]-y[16]-y[17]-y[52]-y[44]-y[46]-de;out[5]=y[38]+y[39]-y[36]-y[37]-y[45]-y[47]-de0;
 out[6]=y[40]-y[17]-y[52]-y[41]-(y[44]-y[45])-(y[46]-y[47])-(de-de0);out[7]=y[42]/(run_m/v);out[8]=y[43]/(run_m/v);
 out[9]=peak;out[10]=peakf;out[11]=accept;out[12]=reject;out[13]=nev;
 out[14]=y[16];out[15]=y[36];out[16]=y[44];out[17]=y[45];out[18]=y[46];out[19]=y[47];out[20]=maxtr;
 out[21]=maxpitch;out[22]=maxroll;out[23]=t;out[24]=fmax(0,t)*v;out[25]=(t+warm_m/v)*v;out[26]=y[48];out[27]=y[49];out[28]=y[52];out[29]=y[17];return invalid;
}

void evaluate(const double*r,const double*dr,int n,double L,double v,double stroke,double amp,double ct,double travel,double stop_k,double offset,double t,const double*y,double*d){
 Model m={r,dr,n,L,v,77170.4861042,77170.4861042*.025,stroke,50.,offset,amp,travel,ct,stop_k,0,.3048};rhs(&m,t,y,d);
}
double evaluate_energy(const double*r,const double*dr,int n,double L,double v,double stroke,double amp,double ct,double travel,double stop_k,double offset,double t,const double*y,int installed){
 Model m={r,dr,n,L,v,77170.4861042,77170.4861042*.025,stroke,50.,offset,amp,travel,ct,stop_k,0,.3048};return energy(&m,t,y,installed);
}
