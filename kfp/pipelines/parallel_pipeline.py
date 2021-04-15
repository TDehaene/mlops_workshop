from kfp import dsl
from kfp import components as comp


@comp.create_component_from_func
def print_op(s: str):
    print(s)

# Create the pipeline
@dsl.pipeline(
    name='Parallel pipeline',
    description='End to end parallelfor pipeline'
)
def parallel_pipeline():
    loop_args = [{'A_a': 1, 'B_b': 2}, {'A_a': 10, 'B_b': 20}]
    with dsl.ParallelFor(loop_args, parallelism=10) as item:
        print_op(item)
        print_op(item.A_a)
        print_op(item.B_b)
