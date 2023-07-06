from dagster import job, op, graph


@op(config_schema={"msg1": str})
def step1(context):
    context.log.info(context.op_config["msg1"])
    

@op(config_schema={"msg2": str})
def step2(context, step1):
    context.log.info(context.op_config["msg2"])


@job
def job():
    step2(step1())


job.execute_in_process(
    run_config={
        "ops": {
            "step1": {"config": {"msg1": "hello"}},
            "step2": {"config": {"msg2": "world"}},
        }
    }
)
