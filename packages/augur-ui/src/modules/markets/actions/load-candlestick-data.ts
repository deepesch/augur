import { augur } from "services/augurjs";
import logError from "utils/log-error";
// TODO: remove these lodash functions.
import { map, mapValues } from "lodash/fp";

const mutatePeriod = map(
  ({
    max,
    min,
    start,
    end,
    startTimestamp,
    volume,
    tokenVolume,
    shareVolume
  }) => ({
    period: startTimestamp * 1000,
    open: parseFloat(start),
    high: parseFloat(max),
    low: parseFloat(min),
    close: parseFloat(end),
    volume: parseFloat(volume),
    shareVolume: parseFloat(shareVolume || tokenVolume)
  })
);

const mutateOutcome = mapValues(mutatePeriod);

/**
 *
 * @typedef {Object} LoadCandleStickDataOptions
 * @property {string} marketId
 * @property {number} outcome
 * @property {number} start
 * @property {number} end
 * @property {number} period
 */

/**
 *
 * @param {LoadCandleStickDataOptions} options
 * @param {function} callback
 */
export const loadCandleStickData = (options = {}, callback: NodeStyleCallback = logError) => {
  augur.augurNode.submitRequest(
    "getMarketPriceCandlesticks",
    options,
    (err: any, data: any) => {
      if (err) return callback(err);

      const mutatedData = mutateOutcome(data);
      callback(null, mutatedData);
    }
  );
};
