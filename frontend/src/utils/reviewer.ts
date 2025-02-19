import { IReviewer } from "@/types/reviewer";
import { reviewerStore } from "@/stores/reviewer";

export function storeReviewer(reviewer: IReviewer) {
  Object.assign(reviewerStore, reviewer);
  localStorage.setItem("reviwer", JSON.stringify(reviewer));
}
