#include <math.h>
#include <string.h>
#include <stdlib.h>
#define NV 44
/* Paired vehicle states, 0..19 installed and 20..39 reference.
   40: direct work difference; 41: direct suspension difference;
   42: installed no-contact time; 43: reference no-contact time.
   Classical RK4 step-doubling with event bracketing, continuous Hermite road.
   Units: m, s, N, J. No tyre damping or suspension stops silently introduced. */
typedef struct {const double *r,*dr; int n;double L,v,k,c,h,spacing,offset,amp,travel,stopratio;} Model;
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
  if(xx<1.1){double z=M_PI*xx/1.1;g[i]=sin(z)*sin(z);gd[i]=m->v*M_PI/1.1*sin(2*z);}
  else {g[i]=0;gd[i]=0;}
 }
}
static void vehicle(const Model *m,const double *s,const double *r,const double *rd,
 const double *g,const double *gd,int installed,double *d,double *force,double *delta){
 const double scale=2000./1840.,ks=22000*scale,cs=1600*scale,kt=200000*scale;
 double load[2]={0,0};memset(d,0,20*sizeof(double));
 for(int i=0;i<4;i++){
  double stat=((i<2?1600*9.81*1.6/5.6:1600*9.81*1.2/5.6)+60*9.81)*scale;
  double gg=installed?g[i]:0;
  delta[i]=stat/kt+r[i]-gg*s[14+i%2]-s[3+i];
  force[i]=kt*fmax(0,delta[i]);load[i%2]+=gg*force[i];
 }
 if(installed)for(int j=0;j<2;j++){
  d[14+j]=(load[j]-m->k*s[14+j])/m->c;
  if(s[14+j]>=m->h && d[14+j]>0)d[14+j]=0;
  if(s[14+j]<=0 && d[14+j]<0)d[14+j]=0;
 }
 for(int j=0;j<7;j++)d[j]=s[j+7];
 for(int i=0;i<4;i++){
  double stat=((i<2?1600*9.81*1.6/5.6:1600*9.81*1.2/5.6)+60*9.81)*scale;
  double z=s[0]+a[i]*s[1]+b[i]*s[2]-s[3+i],zd=s[7]+a[i]*s[8]+b[i]*s[9]-s[10+i];
  double excess=fmax(0,fabs(z)-m->travel);
  double fs=ks*z+cs*zd+(m->travel>0?copysign(ks*m->stopratio*excess,z):0);
  d[7]-=fs/(1600*scale);d[8]-=a[i]*fs/(2400*scale);d[9]-=b[i]*fs/(1800*scale);
  d[10+i]=(fs+force[i]-stat)/(60*scale);
  d[16]+=cs*zd*zd;d[18]+=force[i]*rd[i];
  if(installed)d[19]-=force[i]*s[14+i%2]*gd[i];
 }
 if(installed)d[17]=m->c*(d[14]*d[14]+d[15]*d[15]);
}
static void rhs(const Model*m,double t,const double*y,double*d){
 double r[4],rd[4],g[4],gd[4],f[4],f0[4],dd[4];input(m,t,r,rd,g,gd);
 vehicle(m,y,r,rd,g,gd,1,d,f,dd);vehicle(m,y+20,r,rd,g,gd,0,d+20,f0,dd);
 d[40]=d[18]+d[19]-d[38]-d[39];d[41]=d[16]-d[36];d[42]=d[43]=0;
 for(int j=0;j<4;j++){d[42]+=(f[j]<=0)?.25:0;d[43]+=(f0[j]<=0)?.25:0;}
}
static void rk(const Model*m,double t,const double*y,double h,double*out){
 double k1[NV],k2[NV],k3[NV],k4[NV],z[NV];rhs(m,t,y,k1);
 for(int j=0;j<NV;j++)z[j]=y[j]+h/2*k1[j];rhs(m,t+h/2,z,k2);
 for(int j=0;j<NV;j++)z[j]=y[j]+h/2*k2[j];rhs(m,t+h/2,z,k3);
 for(int j=0;j<NV;j++)z[j]=y[j]+h*k3[j];rhs(m,t+h,z,k4);
 for(int j=0;j<NV;j++)out[j]=y[j]+h/6*(k1[j]+2*k2[j]+2*k3[j]+k4[j]);
}
static void events(const Model*m,double t,const double*y,double*e){
 double r[4],rd[4],g[4],gd[4],f[4],de[4],d[20];input(m,t,r,rd,g,gd);
 vehicle(m,y,r,rd,g,gd,1,d,f,de);for(int j=0;j<4;j++)e[j]=de[j];
 vehicle(m,y+20,r,rd,g,gd,0,d,f,de);for(int j=0;j<4;j++)e[4+j]=de[j];
 e[8]=m->h-y[14];e[9]=m->h-y[15];
 for(int v=0;v<2;v++)for(int j=0;j<4;j++){const double*s=y+20*v;
  double z=s[0]+a[j]*s[1]+b[j]*s[2]-s[3+j];e[10+4*v+j]=m->travel>0?m->travel-fabs(z):1;}
}
static double energy(const Model*m,double t,const double*y,int installed){
 double r[4],rd[4],g[4],gd[4];input(m,t,r,rd,g,gd);
 const double sc=2000./1840.,ks=22000*sc,kt=200000*sc;
 double en=.5*sc*(1600*y[7]*y[7]+2400*y[8]*y[8]+1800*y[9]*y[9]);
 for(int j=0;j<4;j++){
  double stat=((j<2?1600*9.81*1.6/5.6:1600*9.81*1.2/5.6)+60*9.81)*sc;
  double de=fmax(0,stat/kt+r[j]-(installed?g[j]*y[14+j%2]:0)-y[3+j]);
  double z=y[0]+a[j]*y[1]+b[j]*y[2]-y[3+j];
  if(m->travel>0){double ex=fmax(0,fabs(z)-m->travel);en+=.5*ks*m->stopratio*ex*ex;}
  en+=.5*(60*sc*y[10+j]*y[10+j]+ks*z*z+kt*de*de)+stat*y[3+j];
 }
 if(installed)en+=.5*m->k*(y[14]*y[14]+y[15]*y[15]);return en;
}
int simulate(const double*r,const double*dr,int n,double L,double v,double k,double tau,
 double stroke,double density,double offset,double amp,double warm_m,double run_m,
 double rtol,double maxdt,double travel,double stopratio,double *out){
 Model m={r,dr,n,L,v,k,k*tau,stroke,1000/density,offset,amp,travel,stopratio};
 double y[NV]={0},one[NV],half[NV],two[NV],e0[18],e1[18],tmp[NV],ee[18];
 double t=-warm_m/v,end=run_m/v,h=fmin(maxdt,.001),en0=0,ref0=0,peak=0,peakf=0;
 double travelpeak=0;
 long accept=0,reject=0,nev=0;int measured=0;
 while(t<end-1e-11){
  if(!measured && t>=-1e-12){t=0;en0=energy(&m,t,y,1);ref0=energy(&m,t,y+20,0);
   for(int j=16;j<20;j++)y[j]=y[j+20]=0;for(int j=40;j<NV;j++)y[j]=0;measured=1;}
  double boundary=measured?end:0;h=fmin(h,fmin(maxdt,boundary-t));if(h<1e-13)return -2;
  rk(&m,t,y,h,one);events(&m,t,y,e0);events(&m,t+h,one,e1);
  double event_h=h;int hit=-1;
  for(int j=0;j<18;j++){
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
  for(int j=16;j<42;j++)if(j<20 || j>=36){
   double scale=1e-5+rtol*fabs(two[j]-y[j]);
   err=fmax(err,fabs(two[j]-one[j])/(15*scale));
  }
  if(!isfinite(err))return -3;
  if(err>1 && h>1e-10){h*=fmax(.15,.85*pow(err,-.2));reject++;continue;}
  if(two[14]>stroke+1e-9 || two[15]>stroke+1e-9){h*=.5;reject++;continue;}
  memcpy(y,two,sizeof(y));
  for(int j=14;j<16;j++)if(y[j]>stroke){
   if(y[j]-stroke>1e-8){h*=.5;return -4;}y[j]=stroke;
  }
  t+=h;accept++;
  if(measured){peak=fmax(peak,fmax(y[14],y[15]));double rr[4],rd[4],g[4],gd[4],f[4],de[4],d[20];
   input(&m,t,rr,rd,g,gd);vehicle(&m,y,rr,rd,g,gd,1,d,f,de);
   for(int j=0;j<4;j++){peakf=fmax(peakf,f[j]);
  travelpeak=fmax(travelpeak,fabs(y[0]+a[j]*y[1]+b[j]*y[2]-y[3+j]));}}
  h*=err<1e-15?2.0:fmin(2.,fmax(.25,.9*pow(err,-.2)));
  if(accept>20000000)return -5;
 }
 double de=energy(&m,t,y,1)-en0,de0=energy(&m,t,y+20,0)-ref0;
 out[0]=y[17];out[1]=y[40];out[2]=y[41];out[3]=de-de0;
 out[4]=y[18]+y[19]-y[16]-y[17]-de;out[5]=y[38]+y[39]-y[36]-y[37]-de0;
 out[6]=y[40]-y[17]-y[41]-(de-de0);out[7]=y[42]/(run_m/v);out[8]=y[43]/(run_m/v);
 out[9]=peak;out[10]=peakf;out[11]=accept;out[12]=reject;out[13]=nev;
 out[16]=travelpeak;out[14]=y[16];out[15]=y[36];return 0;
}
