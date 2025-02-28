from kfp import dsl
from kfp import components as comp


# The different available cover types
COVER_TYPES = [f'Cover_Type_{n}' for n in range(7)]

# Load the components
prepare_datasets_op = comp.load_component('components/prepare_datasets/component.yaml')
split_data_op = comp.load_component('components/split_data/component.yaml')
preprocess_op = comp.load_component('components/preprocessing/component.yaml')
train_op = comp.load_component('components/training/component.yaml')
evaluate_op = comp.load_component('components/evaluation/component.yaml')


# Create the pipeline
@dsl.pipeline(
    name='End to end pipeline',
    description='End to end XGBoost cover type training pipeline'
)
def end_to_end_pipeline(
    gcs_bucket: str,
    bq_table_name: str = 'covertype_dataset.covertype',
    target_col: str = 'Cover_Type',
    test_size: float = 0.2,
    n_estimators: int = 300,
    learning_rate: float = 0.1,
    scale_pos_weight: str = 'FALSE'
):
    # Get the unique run id that will be assigned by KFP for this run
    # Note: This is a placeholder and will be filled in at runtime
    run_id = f'end_to_end_xgb_train_{dsl.RUN_ID_PLACEHOLDER}'
    gcs_output_path = f'gs://{gcs_bucket}/{run_id}'

    prepare_datasets_task = (
        prepare_datasets_op(
            bq_table_name=bq_table_name,
            gcs_output_path=gcs_output_path,
            target_col=target_col
        )
        .set_cpu_request('500m')
        .set_memory_request('4G')
        .set_display_name('Prepare binary classification datasets')
    )

    for cover_type in COVER_TYPES:
        cover_type_input_path = f'{gcs_output_path}/{cover_type}'
        cover_type_output_path = f'{gcs_output_path}/{cover_type}'

        split_data_task = (
            split_data_op(
                gcs_input_path=cover_type_input_path,
                gcs_output_path=cover_type_output_path,
                test_size=test_size
            )
            .set_cpu_request('500m')
            .set_memory_request('4G')
            .after(prepare_datasets_task)
            .set_display_name(f'Train test split {cover_type}')
        )

        preprocess_task = (
            preprocess_op(
                gcs_input_path=cover_type_input_path,
                gcs_output_path=cover_type_output_path,
                target_col_prefix=target_col
            )
            .set_cpu_request('500m')
            .set_memory_request('4G')
            .after(split_data_task).set_display_name(f'Preprocess data {cover_type}')
        )

        train_task = (
            train_op(
                gcs_input_path=cover_type_input_path,
                gcs_output_path=cover_type_output_path,
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                scale_pos_weight=scale_pos_weight
            )
            .after(preprocess_task)
            .set_cpu_request('1000m')
            .set_memory_request('4G')
            .set_display_name(f'Train XGBoost model {cover_type}')
        )

        evaluate_task = (
            evaluate_op(
                gcs_input_path=cover_type_input_path
            )
            .after(train_task)
            .set_cpu_request('500m')
            .set_memory_request('4G')
            .set_display_name(f'Evaluate XGBoost model {cover_type}')
        )
