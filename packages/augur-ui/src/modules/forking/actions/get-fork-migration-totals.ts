import { augur } from "services/augurjs";
import logError from "utils/log-error";
import calculatePayoutNumeratorsValue from "utils/calculate-payout-numerators-value";
import { AppState } from "store";
import { NodeStyleCallback } from "modules/types";
import { ThunkDispatch } from "redux-thunk";
import { Action } from "redux";

export const getForkMigrationTotals = (
  universeId: string,
  callback: NodeStyleCallback = logError,
) => (dispatch: ThunkDispatch<void, any, Action>, getState: () => AppState) => {
  const { marketsData, universe } = getState();

  augur.api.Universe.getForkingMarket(
    { tx: { to: universeId } },
    (err: any, forkingMarketId: string) => {
      if (err) return callback(err);
      const forkingMarket = marketsData[forkingMarketId];
      augur.augurNode.submitRequest(
        "getForkMigrationTotals",
        {
          parentUniverse: universeId,
        },
        (err: any, result: any) => {
          if (err) return callback(err);
          callback(
            null,
            Object.keys(result).reduce((acc, key) => {
              const cur = result[key];
              const isInvalidKey = "0.5"; // used as indetermine id in market reportable outcomes
              const payoutKey: string | null = calculatePayoutNumeratorsValue(
                forkingMarket,
                cur.payout,
                cur.isInvalid,
              );
              acc[payoutKey == null ? isInvalidKey : payoutKey] = {
                repTotal: cur.repTotal,
                winner: cur.universe === universe.winningChildUniverse,
                isInvalid: !!cur.isInvalid,
              };
              return acc;
            }, {}),
          );
        },
      );
    },
  );
};
