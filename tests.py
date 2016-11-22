from src.core import Solver


def test_solver():
    board_text = '''
       ____l
       t_k_e
       e_a_m
       s_y_m
       t___a
    '''
    board = board_text.strip().split()
    wordlist = ['test', 'kayak', 'lemma']

    s1 = Solver(board, 5, wordlist)
    s1_solution = list(s1.solve())
    assert 'test' not in s1_solution
    assert 'kayak' not in s1_solution
    assert 'lemma' in s1_solution

    s2 = Solver(board, 4, wordlist)
    s2_solution = list(s2.solve())
    assert 'test' in s2_solution
    assert 'kayak' not in s2_solution
    assert 'lemma' in s2_solution


if __name__ == '__main__':
    test_solver()
