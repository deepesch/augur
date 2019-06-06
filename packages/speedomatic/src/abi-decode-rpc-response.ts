import { abiDecodeData } from "./abi-decode-data";

export function abiDecodeRpcResponse(responseType, abiEncodedRpcResponse) {
  const decodedRpcResponse = abiDecodeData([{type: responseType}], abiEncodedRpcResponse)[0];
  return decodedRpcResponse;
}


