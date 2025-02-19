export interface PredictedRankingItem {
  key: number
  data: {
    ranking?: number
    model: string
    score: string
  }
}

export const predictedRankingColumn = { ranking: 'ranking', name: 'model', score: 'score' }

export const predictRanking: PredictedRankingItem[] = [
  { key: 0, data: { model: 'Contriever', score: '0.945' } },
  { key: 1, data: { model: 'SimLm', score: '0.871' } },
  { key: 2, data: { model: 'CoCondenser', score: '0.842' } },
  { key: 3, data: { model: 'Instructor-XL', score: '0.702' } },
]

let list = []
for (let i = 0; i < 50; i++) {
  if (predictRanking[i]) {
    list.push(predictRanking[i])
    list[i].data.ranking = i + 1
  } else {
    let node = {
      key: i,
      data: {
        ranking: i + 1,
        model: 'Model Name',
        score: (1 / (i + 1)).toFixed(3),
      },
    }
    list.push(node)
  }
}
export const data_lists: PredictedRankingItem[] = list
