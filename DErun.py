import DE
#import time
import matplotlib.pyplot as plt
import csv


#startTime = time.time()

popSize = 40
F = 0.8
CR = 0.9
gens = 50

# Stator diameter
DS1 = (380, 460)
# Stator core length
LFe = (300,460)
# Number of parallel wires
PW = (10,25)
# Number of turns
N = (5,20)


optimPar = (DS1, LFe, PW, N)

savePath = r"C:\...\Results"

fig = plt.figure()
ax = plt.subplot()
plt.xlabel("Generations")
plt.ylabel("Cost Value")

try:
    for i in range(5):
        bestIndividual, bestValue, yCostVal = DE.DE(popSize, F, CR, gens, optimPar).optimize()

        print("\n\n\nRun#"+str(i+1))
        print('Best Individual:\n', bestIndividual)
        print('\nBest Value:\n', bestValue)

        with open(savePath+"\DEruns.txt", "a") as f:
            _ = f.write("Run#"+str(i+1))
            _ = f.write('\n\nBest Individual:\n'+str(bestIndividual))
            _ = f.write('\n\nBest Value:\n'+str(bestValue))
            _ = f.write("\n\n\n\n")

        #plt.plot(yCostVal)
        ax.plot(yCostVal)
        fig.savefig(savePath+"\DEruns.png")

        with open(savePath+"\DEruns.csv", "a", newline="") as c:
            writer = csv.writer(c)
            row = ("Run#"+str(i+1),) + yCostVal
            writer.writerow(row)

except Exception as e:
    print("ERROR: ",e)
    with open(savePath+"\ERROR.txt", "w") as err:
        err.write(str(e))


#print('\n\nCode took', time.time() - startTime, 'seconds to run.')
