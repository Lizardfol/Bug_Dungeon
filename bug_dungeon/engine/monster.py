
STAGES = [
    "",
    r"""
   (\_/)
   (o.o)   A tiny gremlin appears...
    > <
""",
    r"""
    (\_/)
    (O_O)  The gremlin grows larger!
   /| |\
    |_|
""",
    r"""
    (\_/)
    (x_x)  The GREMLIN is furious!
   _/| |\_
    /   \
"""
]

def render_monster(fails: int):
    stage = min(fails, len(STAGES)-1)
    print(STAGES[stage])
