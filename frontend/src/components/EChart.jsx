import ReactECharts from 'echarts-for-react'

export default function EChart({ option, height = 380 }) {
  return (
    <ReactECharts
      option={option}
      style={{ height, width: '100%' }}
      notMerge
      lazyUpdate
    />
  )
}

