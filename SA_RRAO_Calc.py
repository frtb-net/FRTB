"""
Calculate Basel III Market Risk Residual Risk Add-On Capital reqirement using the
Standardised Approach within the frtb.net framework

Copyright © 2024 frtb.net limited

Author: Alan Skea, frtb.net limited

Contact us at <info@frtb.net> or via our website at <https://frtb.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pandas as pd

import FRTBCalculator

@FRTBCalculator.registerClass
class MR_RR_SA_RRAO(FRTBCalculator.FRTBCalculator):
    # This is the primary entry point and computes capital for a single risk class
    # at all the necessary correlation levels.  It returns a Dictionary with an entry
    # for RiskClass and an entry for each computed result, such as the capital
    # at each of the correlation levels.  E.g.:
    #   {
    #       'RiskClass' : 'MR_RRAO',
    #       'Medium'    : 123.45,
    #   }
    #
    def calcRiskClassCapital(self, riskClass, df):
        bucketResult = []

        for bucket, bucketSensis in df.groupby('Bucket'):
            bdf = self.prepareData(riskClass, bucketSensis)
            bdf = self.applyRiskWeights(riskClass, bdf)
            bdf = self.collectRiskFactors(riskClass, bdf)  # this ought to be a no-op for RRAO
            bucketResult.extend(self.getBucketCalculator(riskClass, bucket)(riskClass, bucket, bdf))

        buckets = pd.DataFrame(bucketResult)
        return self.aggregateRRAO(riskClass, buckets)


    def getBucketCalculator(self, riskClass, bucket):
        return self.calcBucketRRAO


    def applyRiskWeights(self, riskClass, df):
        RW = self.getConfigItem('RiskWeight')
        df.loc[:, 'RiskWeight'] = df['Bucket'].apply(lambda x: RW[x])
        df.loc[:, 'Capital'] = df['RiskWeight'] * df['NotionalAmount']
        return df
    

    def collectRiskFactors(self, riskClass, df):
        return df


    # Compute RRAO for a single bucket (e.g. Exotic or Non-Exotic)
    #
    def calcBucketRRAO(self, riskClass, bucket, df):
        capital = df['Capital'].sum()
        bucketRRAO = {
            'RiskClass': riskClass,
            'Bucket': bucket,
            'Capital': capital
        }
        return [bucketRRAO]


    def aggregateRRAO(self, riskClass, buckets):
        capitals = []
        # Create capital dictionary
        capital = {}
        capital['RiskClass'] = riskClass
        capital['Correlation'] = 'Medium'
        capital['Capital'] = buckets['Capital'].sum()
        capitals.append(capital)
        return capitals
