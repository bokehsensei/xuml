from subprocess import call
main='''
digraph {state_machine} {{
labelfontname="Source Code Pro,Source Code Pro ExtraLight:style=ExtraLight,Regular";
fontnames="Source Code Pro,Source Code Pro ExtraLight:style=ExtraLight,Regular";
fontsize=24;
fontcolor=white;
/*bgcolor="#0097cb";*/
bgcolor="#606070";
color=white;
size="12!";

node [
    shape=rectangle,
    style=rounded
    fontcolor=white;
    color=white;
];

edge [
    color="#d0d0d0";
    colorscheme=svg;
    fontcolor="#d0d0d0";
];

{body}

}}
'''

initial_state_body='''initial_state [
    label="";
    color="#ffffff";
    shape=circle;
    bgcolor="#b0b0b0";
    style=filled;
];'''

final_state_body='''final_state [
    label="";
    color="#b0b0b0";
    shape=doublecircle;
    bgcolor="#b0b0b0";
    style=filled;
];'''

def dot(state_machine, save=True):
    ''' Output the state machine in DOT format '''
    body = ''
    has_initial_state = False
    has_final_state = False
    initial_state_name = 'initial_state'
    final_state_name = 'destroy'
    for event_name, transitions in state_machine.event_transitions.items():
        for from_state, to_state in transitions.items():
            if not from_state:
                from_state = initial_state_name
                if not has_initial_state:
                    has_initial_state = True
                    body+=initial_state_body
            if not to_state:
                to_state = final_state_name
                if not has_final_state:
                    has_final_state = True
                    body+='{} [shape=doublecircle; color=black;];\n'.format(final_state_name)
            body+='->'.join([from_state, to_state])+'[label={}]'.format(event_name)+';\n'
    output = main.format(
        state_machine=state_machine.__name__,
        body=body
    )

    dot_file = state_machine.__name__ + '.dg'
    svg_file = state_machine.__name__ + '.svg'
    jpg_file = state_machine.__name__ + '.jpg'
    with open(dot_file, 'w') as f:
        print(output, file=f)

    call(['dot', '-Tsvg', dot_file, '-o', svg_file])
    call(['dot', '-Tjpg', dot_file, '-o', jpg_file])
