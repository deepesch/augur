import React from 'react'

import MarketOutcomesList from 'modules/market/components/market-outcomes-list/market-outcomes-list'
import MarketPositionsList from 'modules/market/components/market-positions-list/market-positions-list'

import Styles from 'modules/market/components/market-data/market-data.styles'

const MarketData = p => (
  <section className={Styles.MarketData}>
    <div className={Styles.MarketData__details}>
      <MarketOutcomesList
        marketID={p.marketID}
        outcomes={p.outcomes}
        scalarShareDenomination={p.scalarShareDenomination}
        selectedOutcomes={p.selectedOutcomes}
        updateSelectedOutcomes={p.updateSelectedOutcomes}
        isMobile={p.isMobile}
      />
      <MarketPositionsList
        positions={p.positions}
        openOrders={p.openOrders}
        isMobile={p.isMobile}
      />
    </div>
    <div className={Styles.MarketData__trading}>
      trading
    </div>
  </section>
)

export default MarketData
