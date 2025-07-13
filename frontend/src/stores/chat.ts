import { reactive } from "vue";

export function storeVisibleChat(visibleChat: boolean) {
  localStorage.setItem("visibleChat", JSON.stringify(visibleChat));
}

export const visibleChatStore = reactive({
  visible: JSON.parse(localStorage.getItem("visibleChat") || "false"),
});
