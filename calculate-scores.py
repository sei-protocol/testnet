from collections import defaultdict
from datetime import datetime
import argparse
from heapq import heappop, heappush
import re
from time import sleep
from enum import Enum
from grpc_requests import Client

COSMOS_TX_SERVICE = "cosmos.tx.v1beta1.Service"
GET_TX_METHOD = "GetTx"
COSMOS_GOV_SERVICE = "cosmos.gov.v1beta1.Query"
PROPOSAL_METHOD = "Proposal"

GRPC_CLIENT: Client = None


class Missions(Enum):
    CREATE_VALIDATOR = "create_validator"
    GOV_QUORUM_VOTE = "gov_quorum_vote"
    DELEGATED_TOKENS = "delegated_tokens"
    CW20_IBC_FIRST_50 = "cw20_ibc_first_50"
    COSMOS_ERC20_IBC_FIRST_50 = "cosmos_erc20_ibc_first_50"
    AXELAR_ERC20_IBC_FIRST_50 = "axelar_erc20_ibc_first_50"
    CW20_IBC = "cw20_ibc"
    COSMOS_ERC20_IBC = "cosmos_erc20_ibc"
    AXELAR_ERC20_IBC = "axelar_erc20_ibc"

def get_mission_points(mission):
    POINTS_MAP = {
        Missions.CREATE_VALIDATOR: 40,
        Missions.GOV_QUORUM_VOTE: 5,
        Missions.DELEGATED_TOKENS: 5,
        Missions.CW20_IBC_FIRST_50: 30,
        Missions.COSMOS_ERC20_IBC_FIRST_50: 30,
        Missions.AXELAR_ERC20_IBC_FIRST_50: 30,
        Missions.CW20_IBC: 15,
        Missions.COSMOS_ERC20_IBC: 15,
        Missions.AXELAR_ERC20_IBC: 15,
    }
    return POINTS_MAP.get(mission, 0)

class Score:
    """
    This will store the score consisting of many mission tasks.
    It will deduplicate the missions to prevent scoring twice for the same mission for a discord handle
    """
    def __init__(self, verbose=False):
        self.verbose = verbose
        # will store discord handle -> completed missions set
        self.completed_mission_map = defaultdict(set)

        # heapqs of size 50 that will track the 50 earliest IBC transfers for each category
        self.cw20_ibc_50 = []
        self.cosmos_ibc_50 = []
        self.axelar_ibc_50 = []

        # track tx_hashes we've seen already
        self.seen_tx_hashes = set()

    def generate_scores(self):
        """
        Returns a dictionary of discord_handle -> point score total for that handle
        """
        score_map = defaultdict(int)
        self.update_to_first_50()

        for discord_handle in self.completed_mission_map:
            # iterate through missions and award points
            for mission in list(self.completed_mission_map[discord_handle]):
                score_map[discord_handle] += get_mission_points(mission)

        return score_map

    def add_mission(self, mission_type, tx_hash, discord_handle, data):
        if tx_hash in self.seen_tx_hashes:
            if self.verbose:
                print(f"Reused TX Hash Detected: {tx_hash}")
            return
        self.seen_tx_hashes.add(tx_hash)
        self.completed_mission_map[discord_handle].add(mission_type)
        if mission_type == Missions.CW20_IBC:
            self.add_new_cw20_ibc(discord_handle, *data)
        elif mission_type == Missions.COSMOS_ERC20_IBC:
            self.add_new_cw20_ibc(discord_handle, *data)
        elif mission_type == Missions.AXELAR_ERC20_IBC:
            self.add_new_cw20_ibc(discord_handle, *data)

    def add_new_cw20_ibc(self, discord_handle, height):
        heappush(self.cw20_ibc_50, (-height, discord_handle))
        # update the completed mission map, we'll upgrade the ones that are in heapq at the end
        # currently, this will only count 50 earliest,
        # not the 50 earliest by unique discord handles
        # (not sure if this is a large enough bug in scoring calc to fix)
        # it won't allocate double points, just the 50th unique discord handle IBC transfer would be given reduced points
        while len(self.cw20_ibc_50) > 50:
            heappop(self.cw20_ibc_50)
            # update completed mission map

    def convert_cw20_ibc_to_discord_set(self):
        return set([item[1] for item in self.cw20_ibc_50])

    def add_new_cosmos_ibc(self, discord_handle, height):
        heappush(self.cosmos_ibc_50, (-height, discord_handle))
        # update the completed mission map, we'll upgrade the ones that are in heapq at the end
        # currently, this will only count 50 earliest,
        # not the 50 earliest by unique discord handles
        # (not sure if this is a large enough bug in scoring calc to fix)
        # it won't allocate double points, just the 50th unique discord handle IBC transfer would be given reduced points
        while len(self.cosmos_ibc_50) > 50:
            heappop(self.cosmos_ibc_50)

    def convert_cosmos_ibc_to_discord_set(self):
        return set([item[1] for item in self.cosmos_ibc_50])

    def add_new_axelar_ibc(self, discord_handle, height):
        heappush(self.axelar_ibc_50, (-height, discord_handle))
        # update the completed mission map, we'll upgrade the ones that are in heapq at the end
        # currently, this will only count 50 earliest,
        # not the 50 earliest by unique discord handles
        # (not sure if this is a large enough bug in scoring calc to fix)
        # it won't allocate double points, just the 50th unique discord handle IBC transfer would be given reduced points
        while len(self.axelar_ibc_50) > 50:
            heappop(self.axelar_ibc_50)

    def convert_axelar_ibc_to_discord_set(self):
        return set([item[1] for item in self.axelar_ibc_50])

    def update_to_first_50(self):
        # update first 50 ibc mission
        cw20_set = self.convert_cw20_ibc_to_discord_set()
        cosmos_set = self.convert_cosmos_ibc_to_discord_set()
        axelar_set = self.convert_axelar_ibc_to_discord_set()
        for discord_handle in self.completed_mission_map:
            # replace the "late" items with "first 50" items if they made it early enough after processing txs
            if Missions.CW20_IBC in self.completed_mission_map[discord_handle]:
                if discord_handle in cw20_set:
                    self.completed_mission_map[discord_handle].remove(Missions.CW20_IBC)
                    self.completed_mission_map[discord_handle].add(Missions.CW20_IBC_FIRST_50)
            if Missions.COSMOS_ERC20_IBC in self.completed_mission_map[discord_handle]:
                if discord_handle in cosmos_set:
                    self.completed_mission_map[discord_handle].remove(Missions.COSMOS_ERC20_IBC)
                    self.completed_mission_map[discord_handle].add(Missions.COSMOS_ERC20_IBC_FIRST_50)
            if Missions.AXELAR_ERC20_IBC in self.completed_mission_map[discord_handle]:
                if discord_handle in axelar_set:
                    self.completed_mission_map[discord_handle].remove(Missions.AXELAR_ERC20_IBC)
                    self.completed_mission_map[discord_handle].add(Missions.AXELAR_ERC20_IBC_FIRST_50)

def validate_mission(res, act=1, verbose=False):
    """
    This validates the tx response and tries to extract a completed mission from it
    It will return the type of mission completed if applicable
    It also returns a tuple of data that would be used as positional arguments to register the mission with score object
    """
    type_urls = [m.type_url for m in res.tx.body.messages]
    act1_validator_map = {
        "/cosmos.staking.v1beta1.MsgCreateValidator": validate_create_validator,
        "/cosmos.gov.v1beta1.MsgVote": validate_gov_vote,
    }
    if verbose:
        print(f"Validating type urls: {type_urls}")
    if act == 1:
        for t in type_urls:
            # just use the first one that is in the map, we dont expect multiple missions to be fulfilled in the same tx
            if t in act1_validator_map:
                return act1_validator_map[t](res, verbose)
    return None, ()

def validate_create_validator(res, verbose=False):
    """
    Tries to validate a result as a create validator mission,
    and returns an enum confirming the mission type, or returns None if validation fails
    as well as a data tuple that will be used to register the mission with the score object
    """
    if res.tx_response.code != 0:
        return None, ()

    return Missions.CREATE_VALIDATOR, ()

def validate_gov_vote(res, verbose=False):
    """
    Tries to validate a result as a governance vote towards
    """
    if res.tx_response.code != 0:
        return None, ()

    extracted_proposal_id = None
    logs = res.tx_response.logs
    for log in logs:
        events = log.events
        for e in events:
            if e.type == "proposal_vote":
                attrs = e.attributes
                for a in attrs:
                    if a.key == "proposal_id":
                        extracted_proposal_id = a.value
    if extracted_proposal_id is None:
        return None, ()

    if verbose:
        print(f"Extracted proposal ID: {extracted_proposal_id}")
    # retrieve the info for that proposal to determine if it reached quorum
    request_data = {"proposal_id": extracted_proposal_id}
    # use grpc_requests with a raw query result
    try:
        gov_res = GRPC_CLIENT.request(COSMOS_GOV_SERVICE, PROPOSAL_METHOD, request_data, raw_output=True)
        if gov_res.proposal.status in {3, 4}:
            return Missions.GOV_QUORUM_VOTE, ()
    except Exception as e:
        if verbose:
            print(f"Exception getting gov proposal {extracted_proposal_id}, error: {e}")
        return None, ()

    return None, ()


class FormEntry:
    """
    This will store the data for a row from the google form
    Schema:
    Timestamp,Name,Email,Discord Handle (ie. John#1514),Completed mission,Proof of completion,Proof of completion (Screenshot)
    """
    def __init__(self, linenum, line, verbose=False):
        """
        This will parse a response from the google form responses and convert to usable data
        """
        items = line.split("\t")
        items = [i.strip() for i in items]
        if len(items) > 7:
            # we only expect 7 items, so this means that there were extraneous commas
            print(f"Too many items in line num {linenum}: {items}")
        self.linenum = linenum
        self.timestamp = datetime.strptime(items[0], "%m/%d/%Y %H:%M:%S")
        self.name = items[1]
        self.email = items[2]
        self.discord = items[3]
        self.completed_mission = items[4]
        self.proof_of_completion = items[5]
        self.screenshot = items[6]
        self.extract_tx_hashes()

    def extract_tx_hashes(self):
        matches = re.findall('[A-F0-9]{64}', self.proof_of_completion)
        self.tx_hashes = matches


def is_new_response(line, verbose=False):
    """
    Checks if the line is a new response or a spillover by checking for a timestamp at the start of the line
    break string at the first space, and then if that parses to a date of format `M/DD/YYYY H:MM:SS`we can treat it as a new line
    """
    first_item = line.split("\t")[0].strip()
    try:
        # try parsing datetime, if succeeds, is a new response line, else is spillover
        datetime.strptime(first_item, "%m/%d/%Y %H:%M:%S")
        return True
    except ValueError as e:
        return False

def parse_csv(filepath, limit=-1, verbose=False):
    """
    This will parse the CSV obtained by downloading the google form for seinami testnet points responses
    Returns a list of FormEntry parsed from the google responses
    """
    form_entries = []
    if verbose:
        print(f"Opening file with filepath: {filepath}")
    with open(filepath, "r") as file:
        line_num = 2
        curr_line = ""
        lines = file.readlines()[1:]
        if limit != -1:
            lines = lines[:limit]
        for line in lines:
            if is_new_response(line, verbose):
                # handle previous lines response
                # may need to handle spillover lines
                try:
                    val = FormEntry(line_num, line, verbose)
                    form_entries.append(val)
                except Exception as e:
                    # print error for line + handle error
                    if verbose:
                        print(f"Line number {line_num} had error {str(e)}")
                line_num += 1
                curr_line = line
            else:
                if verbose:
                    print(f"Spillover response: {line}")
                curr_line += line

    if verbose:
        print(f"Processed file, {len(form_entries)} entries parsed")
    return form_entries

def get_tx_info(tx_hash, verbose=False):
    """
    Calls the grpc endpoint to get TX info from tx hash. Gracefully handles errors by returning None for the result
    """
    request_data = {"hash": tx_hash}
    # make request to grpc node to get tx info
    # use grpc_requests with a raw query result
    try:
        res = GRPC_CLIENT.request(COSMOS_TX_SERVICE, GET_TX_METHOD, request_data, raw_output=True)
        return res
    except Exception as e:
        if verbose:
            print(f"Exception with TX Hash {tx_hash}, error: {e}")
        return None


def calculate_scores(filepath, fileout, limit=-1, verbose=False, act=1):
    """
    This takes the form entries from parsed CSV
    queries a node to get TX info by tx hash
    automatically handles the tx info if possible
    and allocates points to a dictionary of discord handles -> scores
    At then end it outputs this mapping of discord handles -> scores to a CSV file
    """
    form_entries = parse_csv(filepath, limit, verbose)
    # The score object will track the scores for all discord handles (and earliest scoring for things like IBC transfers)
    # score object will be resistant to duplicate task completions
    score = Score(verbose)

    for entry in form_entries:
        # iterate through form entries and retrieve tx hash info
        for tx_hash in entry.tx_hashes:
            res = get_tx_info(tx_hash, verbose)
            if res is not None:
                # process the result to allocate points
                # add mission to score object after validating the mission
                mission, data = validate_mission(res, act, verbose)
                if mission is not None:
                    score.add_mission(mission, tx_hash, entry.discord, data)
            else:
                # result is None, maybe report the TX hash as erroring
                pass

            # sleep for quarter second to help reduce load on node
            sleep(0.25)

    totals = score.generate_scores()
    if verbose:
        print(f"Score totals: {totals}")

    totals_sorted = sorted([(discord, totals[discord]) for discord in totals], key=lambda x: x[1], reverse=True)

    with open(fileout, "w") as file:
        for item in totals_sorted:
            file.write(f"{item[0]}, {item[1]}\n")
        file.flush()

    # write totals to file


def main():
    global GRPC_CLIENT
    parser = argparse.ArgumentParser(description="Take in a TSV file of testnet responses to output scoring CSV")
    parser.add_argument('filepath', metavar='filepath', type=str,
                    help='Filepath for csv')
    parser.add_argument("-v", "--verbose", dest="verbose", type=bool, help="Whether verbose output should be shown", required=False, default=False)
    parser.add_argument("--fileout", dest="fileout", type=str, help="What path to write the output file to", required=False, default="./scores_output.csv")
    parser.add_argument("-l", "--limit", dest="limit", type=int, help="How many lines of the CSV to process (includes header line)", required=False, default=-1)
    parser.add_argument("-a", "--act", dest="act", type=int, help="Which act are we processing info for", required=False, default=1)
    parser.add_argument("--grpc_path", dest="grpc_path", type=str, help="What grpc address + port to use", required=False, default="ec2-18-144-13-149.us-west-1.compute.amazonaws.com:9090")
    args = parser.parse_args()

    GRPC_CLIENT = Client.get_by_endpoint(args.grpc_path)
    calculate_scores(args.filepath, args.fileout, args.limit, args.verbose, args.act)

if __name__ == "__main__":
    main()