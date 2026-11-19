from sweep import execute,table
if __name__=='__main__':
 tasks=[('reference',seed,iso,h,2e-6,.0025,1000.,1000.,50.) for seed in range(3101,3117) for iso in 'ABCDEFG' for h in [.005,.01,.025]]
 execute(tasks);table()
