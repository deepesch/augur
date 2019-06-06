export { createAdapter, EthersProviderBlockStreamAdapter } from "./ethers";
import { Block, FilterOptions, Log } from "ethereumjs-blockstream";

export type GetBlockByString = (hash: string) => Promise<Block | null>;

export interface ExtendedLog extends Log {
  transactionIndex?: number;
  removed?: boolean;
  transactionLogIndex?: number;
  address: string;
  data: string;
  topics: string[];
  transactionHash?: string;
}

export interface BlockAndLogStreamerDependencies<T extends Log, B extends Block> {
  getBlockByNumber: GetBlockByString;
  getBlockByHash: GetBlockByString;
  getLogs: (filterOptions: FilterOptions) => Promise<T[]>;
  startPollingForBlocks: (reconcileNewBlock:(block: B) => Promise<void>) => void;
}
