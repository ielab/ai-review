import { reactive } from "vue";
import { IReviewer } from "@/types/reviewer";
import { DEFAULT_REVIEWER_STORE } from "@/defaults/reviewer";

export const reviewerStore: IReviewer = reactive(
  JSON.parse(
    localStorage.getItem("reviwer") || JSON.stringify(DEFAULT_REVIEWER_STORE)
  ) as IReviewer
);

export function cleanReviewerStore() {
  Object.assign(reviewerStore, DEFAULT_REVIEWER_STORE);
}
