import { SyncableDB } from "./SyncableDB";
import { Augur } from "../../Augur";
import { ParsedLog } from "@augurproject/types";
import { DB } from "./DB";

/**
 * Stores event logs for user-specific events.
 */
export class UserSyncableDB extends SyncableDB {
  public readonly user: string;
  private additionalTopics: Array<Array<string | Array<string>>>;

  constructor(augur: Augur, dbController: DB, networkId: number, eventName: string, user: string, numAdditionalTopics: number, userTopicIndicies: Array<number>, idFields: Array<string> = []) {
    super(augur, dbController, networkId, eventName, dbController.getDatabaseName(eventName, user), idFields);
    this.user = user;
    const bytes32User = `0x000000000000000000000000${this.user.substr(2).toLowerCase()}`;
    this.additionalTopics = [];
    for (let userTopicIndex of userTopicIndicies) {
      const topics: Array<string | Array<string>> = [];
      topics.fill("", numAdditionalTopics);
      topics[userTopicIndex] = bytes32User;
      this.additionalTopics.push(topics);
    }
  }

  protected async getLogs(augur: Augur, startBlock: number, endBlock: number): Promise<Array<ParsedLog>> {
    let logs: Array<ParsedLog> = [];
    for (let topics of this.additionalTopics) {
      logs = logs.concat(await augur.events.getLogs(this.eventName, startBlock, endBlock, topics));
    }
    return logs;
  }

  public getFullEventName(): string {
    return `${this.eventName}-${this.user}`;
  }
}
