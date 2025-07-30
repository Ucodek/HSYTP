import numpy as np
from scipy.optimize import linprog
from scipy.optimize import minimize

class Optimizer:
    def __init__(self, mean_return, cov):
        ### NOTE: The bounds are by default (0, None) unless otherwise specified.
        # bounds = None, bounds = [(-0.5, None)]*D, bounds = [(0, None)]*D
        self.mean_return = mean_return
        self.cov = cov
        self.D = len(self.mean_return)
        self.bounds = [(0, 1)] * self.D

    def __get_portfolio_variance(self, weights):
        # return weights[0].dot(weights[1]).dot(weights[0])
        return weights.dot(self.cov).dot(weights)

    def __target_return_constraint(self, weights, target):
        return weights.dot(self.mean_return) - target

    def __portfolio_constraint(self, weights):
        return weights.sum() - 1

    def neg_get_sharpe_ratio(self, weights):
        ret = weights.dot(self.mean_return)
        risk = np.sqrt(weights.dot(self.cov).dot(weights))
        return -(ret - self.risk_free_rate) / risk

    def min_variance_optimizer(self):
        res = minimize(
            fun=self.__get_portfolio_variance,
            # x0=[np.ones(D) / D, cov], # uniform
            x0=np.ones(self.D) / self.D, # uniform
            method='SLSQP',
            constraints={
                'type': 'eq',
                'fun': self.__portfolio_constraint,
            },
            bounds=self.bounds
        )
        # mv_risk = np.sqrt(res.fun)
        mv_weights = res.x
        # mv_ret = mv_weights.dot(self.mean_return)
        return mv_weights
    
    def sharpe_ratio_optimizer(self, risk_free_rate):
        self.risk_free_rate = risk_free_rate
        res = minimize(
            fun=self.neg_get_sharpe_ratio,
            x0=np.ones(self.D) / self.D, # uniform
            method='SLSQP',
            constraints={
                'type': 'eq',
                'fun': self.__portfolio_constraint,
            },
            bounds=self.bounds
        )
        # mv_risk = np.sqrt(-res.fun)
        sr_weights = res.x
        # mv_ret = mv_weights.dot(self.mean_return)
        return sr_weights
    
    def monte_carlo_optimizer(self, N = 10000, risk_free_rate = 10):
        self.risk_free_rate = risk_free_rate
        mc_best_w = None
        mc_best_sr = float('-inf')
        for _ in range(N):
            w = np.random.random(self.D)
            w = w / w.sum()
            sr = self.neg_get_sharpe_ratio(w)
            if sr > mc_best_sr:
                mc_best_sr = sr
                mc_best_w = w
        # mv_risk = np.sqrt(mc_best_sr)
        # mv_ret = mv_weights.dot(self.mean_return)
        return mc_best_w
    