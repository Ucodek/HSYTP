
import numpy as np

class ABC:
    def __init__(self, mean_return, cov, P, limit, lb, ub, MR, method_name, rfr):
        self.methods = {
            'dengeli': self.__neg_sharpe_ratio,
            'garantici': self.__variance,
            'temkinli': self.__neg_sortino_ratio
        }
        
        self.method = self.methods.get(method_name, self.__neg_sharpe_ratio) # Method ismi varsa o methodu uyguluyor method ismi yoksa sharpe ratio'ya göre optimizasyon yapıyor.
        
        self.mean_return = mean_return
        self.cov = cov
        self.risk_free_rate = rfr
        self.D = len(self.mean_return)
        self.P = P  # P is population size
        self.limit = limit
        self.lb = lb  # lower bound for parameters
        self.ub = ub  # upper bound for parameters
        self.MR = MR  # modification rate
        self.evaluationNumber = 0
        self.tmpID = [-1] * self.P
        self.Foods = np.random.uniform(self.lb, self.ub, size = (self.P, self.D))
        self.Foods /= self.Foods.sum(axis=1, keepdims=True) 
        self.solution = np.copy(self.Foods)
        self.f = self.calculateF(self.Foods)
        self.fitness = self.calculate_fitness(self.f)
        self.trial = np.zeros(P)
        self.globalMin = self.f[0]
        self.globalParams = np.copy(self.Foods[0])  # 1st row
        self.scoutBeeCounts = 0

    def create_new(self, index):
        new_sol = np.random.uniform(self.lb, self.ub, self.D)
        self.Foods[index, :] = new_sol
        self.solution[index, :] = np.copy(self.Foods[index, :])
        self.f[index] = self.calculateF(new_sol.reshape(1, -1))
        self.fitness[index] = self.calculate_fitness(self.f[index])
        self.trial[index] = 0
        self.scoutBeeCounts += 1

    def memorizeBestSource(self):
        index = np.argmin(self.f)
        if self.f[index] < self.globalMin:
            self.globalMin = self.f[index]
            self.globalParams = np.copy(self.Foods[index])

    def calculateProbabilities(self):
        maxfit = np.max(self.fitness)
        self.prob = (0.9 / maxfit * self.fitness) + 0.1

    def calculate_fitness(self, fObjV):
        fFitness = np.where(fObjV >= 0, 1 / (fObjV + 1), 1 + np.abs(fObjV))
        return fFitness

    def sendEmployedBees(self):
        for i in range(self.P):  # for each clone
            ar = np.random.rand(self.D)
            param2change = np.where(ar < self.MR)[0]

            neighbour = np.random.randint(0, self.P)
            while neighbour == i:
                neighbour = np.random.randint(0, self.P)

            arr = np.copy(self.Foods[i, :])

            r = -1 + (1 + 1) * np.random.rand()

            arr[param2change] = self.Foods[i, param2change] + r * (self.Foods[i, param2change] - self.Foods[neighbour, param2change])
            arr[param2change] = np.clip(arr[param2change], self.lb, self.ub)
            self.solution[i, :] = arr / np.sum(arr)

    def sendOnLookerBees(self):
        i = 0
        t = 0
        while t < self.P:
            if np.random.rand() < self.prob[i]:
                ar = np.random.rand(self.D)
                param2change = np.where(ar < self.MR)

                neighbour = np.random.randint(self.P)
                while neighbour == i:
                    neighbour = np.random.randint(self.P)

                r = -1 + (1 + 1) * np.random.rand()
                arr = self.Foods[i, param2change] + r * (self.Foods[i, param2change] - self.Foods[neighbour, param2change])
                self.tmpID[t] = i

                arr = np.clip(arr, self.lb, self.ub)
                self.solution[t, param2change] = arr
                self.solution[t, :] /= np.sum(self.solution[t, :])
                t += 1
            i += 1
            if i >= self.P:
                i = 0

    def sendScoutBees(self):
        index = np.argmax(self.trial)
        if self.trial[index] >= self.limit:
            self.create_new(index)

    def __variance(self, weights):
        # return weights[0].dot(weights[1]).dot(weights[0])
        return np.sum(np.dot(weights, self.cov) * weights, axis=1)
    
    def __neg_sortino_ratio(self, weights): # temkinli
        ret = np.dot(weights, self.mean_return)  # Her bir satırda dönüşü hesaplayın
        downside_returns = np.minimum(ret[:, np.newaxis] - self.risk_free_rate, 0)
        downside_deviation = np.sqrt(np.mean(downside_returns**2, axis=1))
        
        # downside_deviation sıfır olan elemanları kontrol edin ve çok büyük bir sayı ile değiştirin
        downside_deviation = np.where(downside_deviation == 0, np.inf, downside_deviation)
        sortino_ratio = -(ret - self.risk_free_rate) / downside_deviation
        return sortino_ratio

    def __neg_sharpe_ratio(self, weights): # dengeli
        ret = weights.dot(self.mean_return)
        risk = np.sqrt(np.sum(np.dot(weights, self.cov) * weights, axis=1))
        return -(ret - self.risk_free_rate) / risk

    def calculateF(self, foods):
        f = self.method(foods)
        self.evaluationNumber += len(f)
        return f



class LearnABC:
    def __init__(self, mean_return, cov, P, limit, lb, ub, MR, evaluationNumber, method_name, rfr):
        self.abc = ABC(mean_return, cov, P, limit, lb, ub, MR, method_name, rfr)
        self.total_numberof_evaluation = evaluationNumber

    def learn(self):
        self.f_values = []
        self.f_values.append(np.min(self.abc.f))
        self.abc.memorizeBestSource()

        # sayac = 0
        while self.abc.evaluationNumber <= self.total_numberof_evaluation:
            self.abc.sendEmployedBees()
            objValSol = self.abc.calculateF(self.abc.solution)
            fitnessSol = self.abc.calculate_fitness(objValSol)
            # a greedy selection is applied between the current solution i and its mutant
            # If the mutant solution is better than the current solution i, replace the solution with the mutant and reset the trial counter of solution i

            ind = np.where(fitnessSol > self.abc.fitness)
            ind2 = np.where(fitnessSol <= self.abc.fitness)
            self.abc.trial[ind] = 0

            self.abc.Foods[ind, :] = self.abc.solution[ind, :]
            self.abc.f[ind] = objValSol[ind]
            self.abc.fitness[ind] = fitnessSol[ind]
            # if the solution i can not be improved, increase its trial counter
            self.abc.trial[ind2] += 1

            self.abc.calculateProbabilities()
            self.abc.sendOnLookerBees()

            objValSol = self.abc.calculateF(self.abc.solution)
            fitnessSol = self.abc.calculate_fitness(objValSol)

            for i in range(self.abc.P):
                t = self.abc.tmpID[i]
                if fitnessSol[i] > self.abc.fitness[t]:
                    self.abc.trial[t] = 0
                    self.abc.Foods[t, :] = self.abc.solution[i, :]
                    self.abc.f[t] = objValSol[i]
                    self.abc.fitness[t] = fitnessSol[i]
                else:
                    self.abc.trial[t] += 1

            self.abc.memorizeBestSource()
            self.abc.sendScoutBees()

            self.f_values.append(np.min(self.abc.f))
            # sayac += 1;
            # if sayac % 5000 == 0: print(f"Sayaç = {sayac}")

        self.net = self.abc.globalParams
        self.globalMin = self.abc.globalMin
        # print(f"Evaluation Number: {self.abc.evaluationNumber}")
        print(f"The number of scout bees: {self.abc.scoutBeeCounts}")


class ABC_Model():
    def __init__(self, lb=0, ub=1, evaluationNumber=200000, limit=20, P=50, MR=0.1):
        '''
        lb is lower bound for parameters to be learned
        ub is upper bound for parameters to be learned
        limit determines whether a scout bee can be created. If a solution cannot be improved up to the limit number, a scout bee is created instead of the solution.
        '''
        self.lb = lb
        self.ub = ub
        self.evaluationNumber = evaluationNumber
        self.limit = limit
        self.P = P
        self.MR = MR

    def fit(self, mean_return, cov, method_name='sharpe-ratio', rfr=None):
        learn = LearnABC(mean_return, cov, self.P, self.limit, self.lb, self.ub, self.MR, self.evaluationNumber, method_name, rfr)
        learn.learn()
        self.net = learn.net
    
    def __str__(self):
        return f"lb={self.lb}, ub={self.ub}, evaNumber={self.evaluationNumber}, P={self.P}, limit={self.limit}, MR={self.MR}, L2={self.L2}"

        
