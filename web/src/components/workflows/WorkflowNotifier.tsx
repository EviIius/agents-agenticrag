import { useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router";
import { toast } from "sonner";
import { useWorkflowActivity } from "@/stores/workflow-activity";
import { useGraphRuns } from "./studio/useGraphRuns";
export default function WorkflowNotifier() {
  const { runs, pausedCount } = useGraphRuns(),
    { pathname } = useLocation(),
    navigate = useNavigate();
  const seen = useRef<Map<string, string>>(new Map()),
    initialized = useRef(false);
  useEffect(() => {
    const active = runs
      .filter(
        (r) =>
          r.mode !== "test" &&
          ["queued", "running", "paused", "cancelling"].includes(r.state),
      )
      .map((r) => ({
        id: r.id,
        name: r.def_name,
        defId: r.def_id,
        state: r.state,
      }));
    if (
      JSON.stringify(active) !==
        JSON.stringify(useWorkflowActivity.getState().active) ||
      pausedCount !== useWorkflowActivity.getState().pausedCount
    )
      useWorkflowActivity.getState().set(active, pausedCount);
    let initialNoticeShown = false;
    for (const run of runs) {
      if (
        (initialized.current || !initialNoticeShown) &&
        run.mode !== "test" &&
        run.state === "paused" &&
        seen.current.get(run.id) !== "paused" &&
        !pathname.includes(run.id) &&
        !(run.def_id && pathname === `/workflows/${run.def_id}`)
      ) {
        initialNoticeShown = true;
        toast(`${run.def_name} is waiting for you.`, {
          id: "workflow-paused",
          action: {
            label: "Open",
            onClick: () =>
              navigate(
                run.def_id
                  ? `/workflows/${run.def_id}/runs/${run.id}`
                  : `/workflows/runs/${run.id}`,
              ),
          },
        });
      }
      seen.current.set(run.id, run.state);
    }
    if (runs.length) initialized.current = true;
  }, [runs, pausedCount, pathname, navigate]);
  return null;
}
