def evaluate_opponent(op_opponent, opponent):
    # TODO some work must be done
    global op_opponent_team_name

    # Idea for AI. Check if the same letters and order from placard team name are the same in the name of the odds
    # portal
    # Usually when the names from odds portal are smaller than placard, are a prefix of first 4 to 5 letters from the
    # longer name.

    if "/" in op_opponent or "/" in opponent:
        op_opponent = op_opponent.split("/")
        opponent = opponent.split("/")

        if len(op_opponent) == len(opponent):
            for i in len(op_opponent):
                if op_opponent[i] in opponent[i]:
                    print("{} is equal {}".format(opp))


    # IF team has / in its name validate both side on its name if there is partial match
    if len(op_opponent.split()) > 1 and opponent in op_opponent:
        op_opponent_team_name = op_opponent
    else:
        op_opponent_team_name = opponent

    # This should be in case placard name team has more characters then the one in odds portal
    while op_opponent_team_name:
        if op_opponent == op_opponent_team_name:
            print("Odds portal name: {}".format(op_opponent_team_name))
            return True
        else:
            op_opponent_team_name = " ".join(op_opponent_team_name.split()[:-1])
    return False
