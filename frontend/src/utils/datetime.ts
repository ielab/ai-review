import dayjs from "dayjs";

export const formatDateTime = (datetime: string) => {
  /**
   * Format datetime to a human-readable format
   * using user's local timezone
   */

  if (!datetime) return "—";
  return dayjs(datetime).format("DD/MM/YYYY, HH:mm:ss");
};
