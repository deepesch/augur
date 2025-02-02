pragma solidity 0.5.4;


import 'ROOT/libraries/CloneFactory.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/reporting/IReputationToken.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/factories/IMarketFactory.sol';
import 'ROOT/IAugur.sol';


contract MarketFactory is CloneFactory, IMarketFactory {
    function createMarket(IAugur _augur, IUniverse _universe, uint256 _endTime, uint256 _feePerCashInAttoCash, uint256 _affiliateFeeDivisor, address _designatedReporterAddress, address _sender, uint256 _numOutcomes, uint256 _numTicks) public returns (IMarket _market) {
        _market = IMarket(createClone(_augur.lookup("Market")));
        require(_augur.isKnownUniverse(_universe));
        IReputationToken _reputationToken = _universe.getReputationToken();
        require(_reputationToken.transfer(address(_market), _reputationToken.balanceOf(address(this))));
        require(_augur.trustedTransfer(ICash(_augur.lookup("Cash")), _sender, address(_market), _universe.getOrCacheValidityBond()));
        _market.initialize(_augur, _universe, _endTime, _feePerCashInAttoCash, _affiliateFeeDivisor, _designatedReporterAddress, _sender, _numOutcomes, _numTicks);
        return _market;
    }
}
