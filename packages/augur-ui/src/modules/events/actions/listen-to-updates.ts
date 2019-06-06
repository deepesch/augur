import { augur } from "services/augurjs";
import {
  handleAugurNodeDisconnect,
  handleEthereumDisconnect
} from "modules/events/actions/disconnect-handlers";
import { handleNewBlock } from "modules/events/actions/handle-new-block";
import {
  handleMarketStateLog,
  handleMarketCreatedLog,
  handleMarketMigratedLog,
  handleTokensTransferredLog,
  handleOrderCreatedLog,
  handleOrderCanceledLog,
  handleOrderFilledLog,
  handleTradingProceedsClaimedLog,
  handleInitialReportSubmittedLog,
  handleInitialReporterRedeemedLog,
  handleMarketFinalizedLog,
  handleDisputeCrowdsourcerCreatedLog,
  handleDisputeCrowdsourcerContributionLog,
  handleDisputeCrowdsourcerCompletedLog,
  handleDisputeCrowdsourcerRedeemedLog,
  handleFeeWindowCreatedLog,
  handleFeeWindowOpenedLog,
  handleTokensMintedLog,
  handleTokensBurnedLog,
  handleFeeWindowRedeemedLog,
  handleCompleteSetsSoldLog,
  handleApprovalLog
} from "modules/events/actions/log-handlers";
import { wrapLogHandler } from "modules/events/actions/wrap-log-handler";
import logError from "utils/log-error";
import { ThunkDispatch } from "redux-thunk";
import { Action } from "redux";
import { AppState } from "store";

export const listenToUpdates = (history: any) => (
  dispatch: ThunkDispatch<void, any, Action>,
  getState: () => AppState
) => {
  augur.events.stopBlockListeners();
  augur.events.stopAugurNodeEventListeners();
  augur.events.startBlockListeners({
    onAdded: (block: any) => dispatch(handleNewBlock(block)),
    onRemoved: (block: any) => dispatch(handleNewBlock(block)),
  });
  augur.events.startAugurNodeEventListeners(
    {
      MarketState: dispatch(wrapLogHandler(handleMarketStateLog)),
      MarketCreated: dispatch(wrapLogHandler(handleMarketCreatedLog)),
      MarketMigrated: dispatch(wrapLogHandler(handleMarketMigratedLog)),
      TokensTransferred: dispatch(wrapLogHandler(handleTokensTransferredLog)),
      OrderCreated: dispatch(wrapLogHandler(handleOrderCreatedLog)),
      OrderCanceled: dispatch(wrapLogHandler(handleOrderCanceledLog)),
      OrderFilled: dispatch(wrapLogHandler(handleOrderFilledLog)),
      TradingProceedsClaimed: dispatch(
        wrapLogHandler(handleTradingProceedsClaimedLog)
      ),
      InitialReportSubmitted: dispatch(
        wrapLogHandler(handleInitialReportSubmittedLog)
      ),
      InitialReporterRedeemed: dispatch(
        wrapLogHandler(handleInitialReporterRedeemedLog)
      ),
      MarketFinalized: dispatch(wrapLogHandler(handleMarketFinalizedLog)),
      DisputeCrowdsourcerCreated: dispatch(
        wrapLogHandler(handleDisputeCrowdsourcerCreatedLog)
      ),
      DisputeCrowdsourcerContribution: dispatch(
        wrapLogHandler(handleDisputeCrowdsourcerContributionLog)
      ),
      DisputeCrowdsourcerCompleted: dispatch(
        wrapLogHandler(handleDisputeCrowdsourcerCompletedLog)
      ),
      DisputeCrowdsourcerRedeemed: dispatch(
        wrapLogHandler(handleDisputeCrowdsourcerRedeemedLog)
      ),
      UniverseForked: dispatch(wrapLogHandler()),
      CompleteSetsPurchased: dispatch(wrapLogHandler()),
      CompleteSetsSold: dispatch(wrapLogHandler(handleCompleteSetsSoldLog)),
      TokensMinted: dispatch(wrapLogHandler(handleTokensMintedLog)),
      TokensBurned: dispatch(wrapLogHandler(handleTokensBurnedLog)),
      FeeWindowCreated: dispatch(wrapLogHandler(handleFeeWindowCreatedLog)),
      FeeWindowOpened: dispatch(wrapLogHandler(handleFeeWindowOpenedLog)),
      InitialReporterTransferred: dispatch(wrapLogHandler()),
      TimestampSet: dispatch(wrapLogHandler()),
      FeeWindowRedeemed: dispatch(wrapLogHandler(handleFeeWindowRedeemedLog)),
      UniverseCreated: dispatch(wrapLogHandler()),
      Approval: dispatch(wrapLogHandler(handleApprovalLog)),
    },
    logError
  );
  augur.events.nodes.augur.on("disconnect", (event: any) =>
    dispatch(handleAugurNodeDisconnect(history, event))
  );
  augur.events.nodes.ethereum.on("disconnect", (event: any) =>
    dispatch(handleEthereumDisconnect(history, event))
  );
};
