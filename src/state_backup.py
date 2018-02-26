import os
import os.path
import pickle


def load_state(server_id):
    state_backup = './state_backup/{}.txt'.format(server_id)
    if not os.path.exists(state_backup):
        state = dict(
                decided_log={},
                promised_proposal_id=None,
                accepted_proposal_id={},
                accepted_proposal_val={},
                accepted_client_info={}
            )
        save_state(server_id, state)

    with open(state_backup) as f:
        state = pickle.load(f)
        return state


def save_state(server_id, state):
    state_backup = './state_backup/{}.txt'.format(server_id)
    tmp = state_backup + '.tmp'
    with open(tmp, 'w') as f:
        pickle.dump(state, f)
        f.flush()
        os.fsync(f.fileno())
    os.rename(tmp, state_backup)
