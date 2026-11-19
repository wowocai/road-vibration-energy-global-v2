#include <math.h>
#include <stdint.h>
// Coordinates relative to static equilibrium: heave, pitch, roll, four wheels.
static inline double rhs(const double *s,const double *r,double ks,double cs,double kt,
                          double *d, int unilateral) {
  const double m=2000./1840.;
  const double a[4]={1.2,1.2,-1.6,-1.6}, b[4]={-.8,.8,-.8,.8};
  double su=0, pi=0, ro=0, loss=0;
  for(int j=0;j<7;j++)d[j]=s[j+7];
  for(int i=0;i<4;i++){
    const double fs0=(i<2?1600.*9.81*1.6/5.6:1600.*9.81*1.2/5.6)+60.*9.81;
    const double stat=fs0*m;
    double sl=d[0]+a[i]*d[1]+b[i]*d[2]-d[i+3];
    double fs=ks*(s[0]+a[i]*s[1]+b[i]*s[2]-s[i+3])+cs*sl;
    double f=stat+kt*(r[i]-s[i+3]);
    if(unilateral && f<0)f=0;
    d[i+10]=(fs+f-stat)/(60.*m);
    su+=fs; pi+=a[i]*fs; ro+=b[i]*fs; loss+=cs*sl*sl;
  }
  d[7]=-su/(1600.*m);d[8]=-pi/(2400.*m);d[9]=-ro/(1800.*m);
  return loss;
}
double run(const double *roads, int n, int warm, double dt, int mode, int unilateral, double *force,
           double *balance) {
  const double m=2000./1840., factor=mode?1.:m;
  const double ks=22000.*factor,cs=1600.*factor,kt=200000.*factor;
  const double fs0[4]={(1600.*9.81*1.6/5.6+60.*9.81)*m,(1600.*9.81*1.6/5.6+60.*9.81)*m,
                       (1600.*9.81*1.2/5.6+60.*9.81)*m,(1600.*9.81*1.2/5.6+60.*9.81)*m};
  const double a[4]={1.2,1.2,-1.6,-1.6},b[4]={-.8,.8,-.8,.8};
  double s[14]={0}, k1[14],k2[14],k3[14],k4[14],q[14];
  double diss=0, roadwork=0, estart=0, eend=0;
  for(int j=-warm;j<=n;j++) {
    int ix=j%n; if(ix<0) ix+=n;
    const double *r=roads+8*ix, *rh=r+4, *rn=ix+1<n?r+8:roads;
    if(j==0 || j==n){
      double energy=.5*m*(1600*s[7]*s[7]+2400*s[8]*s[8]+1800*s[9]*s[9]);
      for(int i=0;i<4;i++){
        double c=fs0[i]/kt+r[i]-s[i+3];
        if(unilateral && c<0)c=0;
        double sd=s[0]+a[i]*s[1]+b[i]*s[2]-s[i+3];
        energy+=.5*(60*m*s[10+i]*s[10+i]+ks*sd*sd+kt*c*c)+fs0[i]*s[i+3];
      }
      if(j==0)estart=energy; else {eend=energy;break;}
    }
    if(j>=0)for(int i=0;i<4;i++){
      double f=fs0[i]+kt*(r[i]-s[i+3]);
      force[j*4+i]=(unilateral && f<0)?0:f;
    }
    double p1=rhs(s,r,ks,cs,kt,k1,unilateral);
    for(int i=0;i<14;i++)q[i]=s[i]+.5*dt*k1[i];
    double p2=rhs(q,rh,ks,cs,kt,k2,unilateral);
    if(j>=0)for(int i=0;i<4;i++) {
      double f=fs0[i]+kt*(rh[i]-q[i+3]);
      roadwork+=(unilateral && f<0?0:f)*(rn[i]-r[i]);
    }
    for(int i=0;i<14;i++)q[i]=s[i]+.5*dt*k2[i];
    double p3=rhs(q,rh,ks,cs,kt,k3,unilateral);
    for(int i=0;i<14;i++)q[i]=s[i]+dt*k3[i];
    double p4=rhs(q,rn,ks,cs,kt,k4,unilateral);
    for(int i=0;i<14;i++)s[i]+=dt/6.*(k1[i]+2*k2[i]+2*k3[i]+k4[i]);
    if(j>=0)diss+=dt/6.*(p1+2*p2+2*p3+p4);
  }
  *balance=roadwork-diss-(eend-estart);
  return diss;
}
