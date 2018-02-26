import os
import os.path
import pickle

def load_state(state_backup):
    # if not os.path.exists(state_backup):
    #     state = dict(
    #             decided_log={},
    #             promised_proposal_id=None,
    #             accepted_proposal_id={},
    #             accepted_proposal_val={},
    #             accepted_client_info={}
    #         )
    #     save_state(state_backup, state)
    # else:
    #     print "Recovering server"

    with open(state_backup) as f:
        state = pickle.load(f)
        return state


def save_state(state_backup, state):
    tmp = state_backup + '.tmp'
    with open(tmp, 'w') as f:
        pickle.dump(state, f)
        f.flush()
        os.fsync(f.fileno())
    os.rename(tmp, state_backup)


def get_state_backup(server_id, state_backup_folder):
    return state_backup_folder + '/{}.pkl'.format(server_id)
