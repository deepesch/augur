import { connect } from "react-redux";
import { updateModal } from "modules/modal/actions/update-modal";
import { Transactions } from "modules/account/components/transactions";
import {
  NETWORK_IDS,
  MODAL_WITHDRAW,
  MODAL_REP_FAUCET,
  MODAL_DAI_FAUCET,
  MODAL_DEPOSIT,
  MODAL_TRANSACTIONS,
} from "modules/common/constants";
import { AppState } from "store";
import { ThunkDispatch } from "redux-thunk";
import { Action } from "redux";

const mapStateToProps = (state: AppState) => ({
  isMainnet: state.connection.augurNodeNetworkId === NETWORK_IDS.Mainnet,
});

const mapDispatchToProps = (dispatch: ThunkDispatch<void, any, Action>) => ({
  repFaucet: () => dispatch(updateModal({ type: MODAL_REP_FAUCET })),
  daiFaucet: () => dispatch(updateModal({ type: MODAL_DAI_FAUCET })),
  deposit: () => dispatch(updateModal({ type: MODAL_DEPOSIT })),
  withdraw: () => dispatch(updateModal({ type: MODAL_WITHDRAW })),
  transactions: () => dispatch(updateModal({ type: MODAL_TRANSACTIONS })),
});

const TransactionsContainer = connect(
  mapStateToProps,
  mapDispatchToProps,
)(Transactions);

export default TransactionsContainer;
