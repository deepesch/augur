import React from "react";

import * as constants from "modules/common/constants";
import { createBigNumber } from "utils/create-big-number";
import { EthIcon } from "modules/common/icons";
import ProfitLossChart from "modules/account/components/profit-loss-chart";
import { MovementLabel } from "modules/common/labels";
import Styles from "modules/account/components/overview-chart.styles.less";
import { formatEther } from "utils/format-number";
import { SizeTypes } from "modules/types";

const ALL_TIME = 3;
export interface OverviewChartProps {
  universe: string;
  currentAugurTimestamp: number;
  timeframe: number;
  getProfitLoss: Function;
}

interface TimeFrameOption {
  label: string;
  periodInterval: number;
  id: number;
}

export interface UserTimeRangeData {
  timestamp: number;
  realized: number;
  realizedPercent: number;
  totalCost: number;
  length: any;
}

interface OverviewChartState {
  profitLossData: Array<Array<number>>;
  profitLossChange: string | null;
  profitLossValue: string | null;
  profitLossChangeHasValue: boolean;
  noTrades: boolean;
}

const BEGINNING_START_TIME = 1530366577;
export default class OverviewChart extends React.Component<
  OverviewChartProps,
  OverviewChartState
> {
  state: OverviewChartState = {
    profitLossData: [],
    profitLossChange: null,
    profitLossValue: null,
    profitLossChangeHasValue: false,
    noTrades: true,
  };

  public container: object | null = null;

  componentDidMount = () => {
    const timeRangeDataConfig =
      constants.TIMEFRAME_OPTIONS[this.props.timeframe];
    this.getChartData(timeRangeDataConfig);
  };

  componentDidUpdate = (nextProps: OverviewChartProps) => {
    if (nextProps.timeframe !== this.props.timeframe) {
      const timeRangeDataConfig =
        constants.TIMEFRAME_OPTIONS[this.props.timeframe];
      this.getChartData(timeRangeDataConfig);
    }
  };

  getChartData = (timeRangeDataConfig: TimeFrameOption) => {
    const { universe, currentAugurTimestamp } = this.props;
    const endTime = null;
    let startTime: number | null =
      currentAugurTimestamp - timeRangeDataConfig.periodInterval;
    if (timeRangeDataConfig.id === ALL_TIME) {
      startTime = BEGINNING_START_TIME;
    }
    this.props.getProfitLoss(
      universe,
      startTime,
      endTime,
      null,
      null,
      (err: string, data: Array<UserTimeRangeData>) => {
        if (err) return console.log("Error:", err);
        const noTrades = data
          .reduce(
            (p, d) => createBigNumber(d.totalCost || constants.ZERO).plus(p),
            constants.ZERO,
          )
          .eq(constants.ZERO);
        let profitLossData: Array<Array<number>> = [];

        const lastData =
          data.length > 0
            ? data[data.length - 1]
            : { realized: 0, realizedPercent: 0 };

        const chartValues = data.reduce(
          (p, d) => ({
            ...p,
            [d.timestamp * 1000]: createBigNumber(d.realized).toNumber()
          }),
          {}
        );

        profitLossData = profitLossData.concat(
          Object.keys(chartValues).reduce(
            (p, t): any => [...p, [parseInt(t, 10), chartValues[t]]],
            [],
          ),
        );

        profitLossData.push([
          currentAugurTimestamp * 1000,
          createBigNumber(data[data.length - 1].realized).toNumber()
        ]);

        this.setState({
          profitLossData,
          profitLossChange: formatEther(lastData.realizedPercent || 0)
            .formatted,
          profitLossChangeHasValue: !createBigNumber(
            lastData.realizedPercent || 0
          ).eq(constants.ZERO),
          profitLossValue: formatEther(lastData.realized).formatted,
          noTrades,
        });
      },
    );
  }

  render() {
    const {
      profitLossData,
      profitLossChange,
      profitLossValue,
      profitLossChangeHasValue,
      noTrades,
    } = this.state;
    let content: any = null;

    if (noTrades) {
      content = (
        <>
          <div>{constants.PROFIT_LOSS_CHART_TITLE}</div>
          <span>No Trading Activity to date</span>
        </>
      );
    } else {
      content = (
        <>
          <div>{constants.PROFIT_LOSS_CHART_TITLE}</div>
          <div>
            <MovementLabel
              showColors
              showIcon={profitLossChangeHasValue}
              showPlusMinus
              showBrackets
              value={Number(profitLossChange)}
              size={SizeTypes.NORMAL}
            />
          </div>
          <div>
            {profitLossValue}
            {EthIcon}
          </div>
          <ProfitLossChart
            // @ts-ignore
            data={profitLossData}
            // @ts-ignore
            width={this.container.clientWidth}
          />
        </>
      );
    }
    return (
      <div
        className={Styles.OverviewChart}
        ref={(container) => {
          this.container = container;
        }}
      >
        {content}
      </div>
    );
  }
}
