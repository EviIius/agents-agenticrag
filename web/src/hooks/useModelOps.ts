import { useRef, useState, type Dispatch, type SetStateAction } from "react";
import type { QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, type Chat, type Detail, type Model } from "@/lib/api";
export function useModelOps({
  query,
  chatId,
  setSelected,
}: {
  query: QueryClient;
  chatId?: string;
  setSelected: Dispatch<SetStateAction<Model | undefined>>;
}) {
  const modelOperation = useRef(false);
  const [loadingModel, setLoadingModel] = useState<string | null>(null);
  const operateModel = async (model: Model, unload = false) => {
    if (modelOperation.current) return;
    modelOperation.current = true;
    setLoadingModel(model.connection_id + model.model_id);
    const notice = toast.loading(
      `${unload ? "Ejecting" : "Loading"} ${model.display_name}…`,
    );
    try {
      await api(unload ? "/models/unload" : "/models/load", {
        connection_id: model.connection_id,
        model_id: model.model_id,
      });
      query.setQueryData(
        ["models"],
        await api<Model[]>("/models?refresh=true"),
      );
      void query.invalidateQueries({ queryKey: ["context", chatId] });
      toast.success(`${model.display_name} ${unload ? "ejected" : "loaded"}`, {
        id: notice,
      });
    } catch (e) {
      toast.error(
        `Couldn’t ${unload ? "eject" : "load"} ${model.display_name}`,
        { id: notice, description: String(e) },
      );
    } finally {
      modelOperation.current = false;
      setLoadingModel(null);
    }
  };
  const changeModel = async (model: Model) => {
    if (modelOperation.current) return;
    try {
      if (chatId) {
        const updated = await api<Chat>(
          "/chats/" + chatId,
          {
            connection_id: model.connection_id,
            model_id: model.model_id,
          },
          "PATCH",
        );
        query.setQueryData<Detail>(
          ["chat", chatId],
          (previous) => previous && { ...previous, chat: updated },
        );
        void query.invalidateQueries({ queryKey: ["context", chatId] });
      }
      setSelected(model);
      if (!model.loaded) await operateModel(model);
    } catch (e) {
      toast.error("Couldn’t switch models", { description: String(e) });
    }
  };
  return { modelOperation, loadingModel, operateModel, changeModel };
}
