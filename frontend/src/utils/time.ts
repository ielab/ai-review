import dayjs from 'dayjs'

export const getTimeDifference = (from: string, to: string) => {
  const fromTime = dayjs(from)
  const toTime = dayjs(to)
  const diff = toTime.diff(fromTime, 'second')
  // Format to HH:MM:SS
  const hours = String(Math.floor(diff / 3600)).padStart(2, '0')
  const minutes = String(Math.floor((diff % 3600) / 60)).padStart(2, '0')
  const seconds = String(diff % 60).padStart(2, '0')
  if ([hours, minutes, seconds].includes('NaN')) return 'N/A'
  return `${hours}:${minutes}:${seconds}`
}
