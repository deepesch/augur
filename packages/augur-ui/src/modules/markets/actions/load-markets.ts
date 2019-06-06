import { augur } from "services/augurjs";
import logError from "utils/log-error";
import { parallel } from "async";
import {
  MARKET_CREATION_TIME,
  MARKET_END_DATE,
  MARKET_RECENTLY_TRADED,
  MARKET_FEE,
  MARKET_OPEN_INTEREST,
  MARKET_REPORTING,
  MARKET_CLOSED,
  REPORTING_STATE,
} from "modules/common-elements/constants";
import { updateMarketsData } from "modules/markets/actions/update-markets-data";
import { NodeStyleCallback } from "modules/types";
import { ThunkDispatch } from "redux-thunk";
import { Action } from "redux";
import { AppState } from "store";

// NOTE -- We ONLY load the market ids during this step.
// From here we populate the marketsData
export const loadMarkets = (type: any, callback: NodeStyleCallback = logError) => (
  dispatch: ThunkDispatch<void, any, Action>,
  getState: () => AppState
) => {
  const { universe } = getState();
  const params = { universe: universe.id };

  augur.markets.getMarkets(params, (err: any, marketsArray: any) => {
    if (err) return callback(err);

    const marketsData = marketsArray.reduce(
      (p: any, id: string) => ({
        ...p,
        [id]: { id },
      }),
      {}
    );

    dispatch(updateMarketsData(marketsData));
    callback(null, marketsArray);
  });
};

export const loadMarketsByFilter = (filterOptions: any, cb:Function = () => {}) => (
  dispatch: ThunkDispatch<void, any, Action>,
  getState: () => AppState
) => {
  const { universe } = getState();
  const filter: any[] = [];
  const sort: any = {};
  const parallelParams: any = {};
  switch (filterOptions.sort) {
    case MARKET_RECENTLY_TRADED: {
      // Sort By Recently Traded:
      sort.sortBy = "lastTradeTime";
      sort.isSortDescending = true;
      break;
    }
    case MARKET_END_DATE: {
      // Sort By End Date (soonest first):
      sort.sortBy = "endTime";
      sort.isSortDescending = false;
      break;
    }
    case MARKET_CREATION_TIME: {
      // Sort By Creation Date (most recent first):
      sort.sortBy = "creationBlockNumber";
      sort.isSortDescending = true;
      break;
    }
    case MARKET_FEE: {
      // Sort By Fee (lowest first):
      sort.sortBy = "marketCreatorFeeRate";
      sort.isSortDescending = false;
      break;
    }
    case MARKET_OPEN_INTEREST: {
      sort.sortBy = "openInterest";
      sort.isSortDescending = true;
      break;
    }
    default: {
      // Sort By Volume:
      // leave defaults
      break;
    }
  }

  const params = {
    universe: universe.id,
    category: filterOptions.category,
    search: filterOptions.search,
    maxFee: parseFloat(filterOptions.maxFee),
    hasOrders: filterOptions.hasOrders,
    ...sort,
  };
  switch (filterOptions.filter) {
    case MARKET_REPORTING: {
      // reporting markets only:
      filter.push([
        REPORTING_STATE.DESIGNATED_REPORTING,
        REPORTING_STATE.OPEN_REPORTING,
        REPORTING_STATE.CROWDSOURCING_DISPUTE,
        REPORTING_STATE.AWAITING_NEXT_WINDOW,
        REPORTING_STATE.AWAITING_FORK_MIGRATION,
      ]);
      filter.forEach(filterType => {
        parallelParams[filterType] = (next: Function) =>
          augur.markets.getMarkets(
            { ...params, reportingState: filterType },
            next
          );
      });
      break;
    }
    case MARKET_CLOSED: {
      // resolved markets only:
      filter.push([
        REPORTING_STATE.AWAITING_FINALIZATION,
        REPORTING_STATE.FINALIZED,
      ]);
      filter.forEach(filterType => {
        parallelParams[filterType] = (next: Function) =>
          augur.markets.getMarkets(
            { ...params, reportingState: filterType },
            next
          );
      });
      break;
    }
    default: {
      // open markets only:
      filter.push(REPORTING_STATE.PRE_REPORTING);
      filter.forEach(filterType => {
        parallelParams[filterType] = (next: Function) =>
          augur.markets.getMarkets(
            { ...params, reportingState: filterType },
            next
          );
      });
      break;
    }
  }
  parallel(parallelParams, (err: any, filteredMarkets: any) => {
    let finalizedMarketList: any[] = [];
    if (err) return cb(err);
    filter.forEach(filterType => {
      if (
        filteredMarkets[filterType] &&
        filteredMarkets[filterType].length > 0
      ) {
        finalizedMarketList = finalizedMarketList.concat(
          filteredMarkets[filterType]
        );
      }
    });

    return cb(null, finalizedMarketList);
  });
};
