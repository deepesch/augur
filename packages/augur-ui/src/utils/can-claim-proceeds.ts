import { createBigNumber } from "utils/create-big-number";
import { CONTRACT_INTERVAL } from "modules/common/constants";

// Check that the CLAIM_PROCEEDS_WAIT_TIME has passed since finalization
export default function canClaimProceeds(
  finalizationTime: number,
  outstandingReturns: number,
  currentTimestamp: number,
): boolean {
  let canClaim = false;
  if (finalizationTime && outstandingReturns && currentTimestamp) {
    const endTimestamp = createBigNumber(finalizationTime).plus(
      createBigNumber(CONTRACT_INTERVAL.CLAIM_PROCEEDS_WAIT_TIME),
    );
    const timeHasPassed = createBigNumber(currentTimestamp).minus(endTimestamp);
    canClaim = timeHasPassed.toNumber() > 0;
  }
  return canClaim;
}
