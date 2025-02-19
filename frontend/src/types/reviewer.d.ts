export interface IReviewer {
  pre: boolean;
  co: boolean;
  post: boolean;
  level: "low" | "high" | string;
  visibleChat: boolean;
}
