import debounce from "utils/debounce";
import { connectAugur } from "modules/app/actions/init-augur";
import { updateModal } from "modules/modal/actions/update-modal";
import { MODAL_NETWORK_DISCONNECTED } from "modules/common/constants";
import { closeModal } from "modules/modal/actions/close-modal";
import { ThunkDispatch } from "redux-thunk";
import { Action } from "redux";
import { AppState } from "store";

const RETRY_TIMER = 3000; // attempt re-initAugur every 3 seconds.

export const reInitAugur = (history: any) => (
  dispatch: ThunkDispatch<void, any, Action>,
  getState: () => AppState
) => {
  const debounceCall = debounce((callback = cb) => {
    const { connection, env } = getState();
    if (!connection.isConnected || !connection.isConnectedToAugurNode) {
      dispatch(
        updateModal({ type: MODAL_NETWORK_DISCONNECTED, connection, env })
      );
      if (connection.isReconnectionPaused) {
        // reconnection has been set to paused, recursive call instead
        callback(connection.isReconnectionPaused);
      } else {
        // reconnection isn't paused, retry connectAugur
        dispatch(connectAugur(history, env, false, callback));
      }
    } else {
      dispatch(closeModal());
    }
  }, RETRY_TIMER);
  const cb = (err: any, connection: any) => {
    // both args should be undefined if we are connected.
    if (!err && !connection) return;
    if (err || !connection.augurNode || !connection.ethereumNode) {
      debounceCall(cb);
    }
  };
  debounceCall(cb);
};
