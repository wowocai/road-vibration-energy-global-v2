#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <vector>
#include <iomanip>
int main(int argc,char**argv){
 std::ifstream f(argv[1],std::ios::binary);int n=525600;std::vector<double> g(n),l(n);f.read((char*)g.data(),n*8);f.read((char*)l.data(),n*8);
 double C=std::stod(argv[2])*1000,eta=std::sqrt(.85),cap=.8*C,pmax=5000./60, soc=0;
 double imp=0,served=0,spill=0,loss=0,start=0;long full=0;int warm=0;
 for(int yr=0;yr<1000;yr++){
  start=soc;imp=served=spill=loss=0;full=0;
  for(int t=0;t<n;t++){
   double direct=std::min(g[t],l[t]),supply=direct;
   if(g[t]>l[t]){double q=std::min({g[t]-l[t],pmax,(cap-soc)/eta});soc+=q*eta;spill+=g[t]-l[t]-q;loss+=q*(1-eta);}
   else {double q=std::min({l[t]-g[t],pmax,soc*eta});soc-=q/eta;supply+=q;loss+=q/eta-q;}
   served+=supply;imp+=l[t]-supply;if(supply>=l[t]-1e-9)full++;
  }
  if(std::abs(soc-start)<1e-6){warm=yr+1;break;}warm=yr+1;
 }
 std::cout<<std::setprecision(14)<<imp/1000<<","<<served/1000<<","<<spill/1000<<","<<loss/1000<<","<<double(full)/n<<","<<start<<","<<soc<<","<<warm<<"\n";
}
