import { loadMarketsInfoIfNotLoaded } from "modules/markets/actions/load-markets-info";
import { Favorite } from "modules/types";
import { ThunkDispatch } from "redux-thunk";
import { Action } from "redux";
import { AppState } from "store";

export const UPDATE_FAVORITES = "UPDATE_FAVORITES";
export const TOGGLE_FAVORITE = "TOGGLE_FAVORITE";

export const updateFavorites = (favorites: Array<Favorite>) => ({
  type: UPDATE_FAVORITES,
  data: { favorites }
});

const toggleFavoriteAction = (marketId: string, timestamp: number) => ({
  type: TOGGLE_FAVORITE,
  data: { marketId, timestamp }
});

export const toggleFavorite = (marketId: string) => (
  dispatch: ThunkDispatch<void, any, Action>,
  getState: () => AppState
) => {
  const { blockchain } = getState();
  dispatch(toggleFavoriteAction(marketId, blockchain.currentAugurTimestamp));
};

export const loadFavoritesMarkets = (favorites: Array<Favorite>) => (
  dispatch: ThunkDispatch<void, any, Action>
) => {
  if (favorites) {
    dispatch(
      loadMarketsInfoIfNotLoaded(Object.keys(favorites), () => {
        dispatch(updateFavorites(favorites));
      })
    );
  }
};
