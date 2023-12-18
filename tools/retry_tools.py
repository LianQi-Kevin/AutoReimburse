import asyncio
import functools
import time
from typing import Type


class MaxRetryException(Exception):
    """最大重试次数异常"""
    pass


class MaxTimeoutException(Exception):
    """最大超时异常"""
    pass


def task_retry(
        max_retry_count: int = 5,
        time_interval: int = 2,
        max_timeout: int = None,
        catch_exc: Type[BaseException] = Exception
):
    """
    任务重试装饰器
    Args:
        max_retry_count: 最大重试次数 默认 5 次
        time_interval: 每次重试间隔 默认 2s
        max_timeout: 最大超时时间，单位s 默认为 None,
        catch_exc: 指定捕获的异常类用于特定的异常重试 默认捕获 Exception
    """

    def _task_retry(task_func):

        @functools.wraps(task_func)
        def sync_wrapper(*args, **kwargs):
            # 函数循环重试
            start_time = time.time()
            for retry_count in range(max_retry_count):
                print(f"execute count {retry_count + 1}")
                use_time = time.time() - start_time
                if max_timeout and use_time > max_timeout:
                    # 超出最大超时时间
                    raise MaxTimeoutException(f"execute timeout, use time {use_time}s, max timeout {max_timeout}")

                try:
                    task_ret = task_func(*args, **kwargs)
                    return task_ret
                except catch_exc as e:
                    print(f"fail {str(e)}")
                    time.sleep(time_interval)
            else:
                # 超过最大重试次数, 抛异常终止
                raise MaxRetryException(f"超过最大重试次数失败, max_retry_count {max_retry_count}")

        @functools.wraps(task_func)
        async def async_wrapper(*args, **kwargs):
            # 异步循环重试
            start_time = time.time()
            for retry_count in range(max_retry_count):
                print(f"execute count {retry_count + 1}")
                use_time = time.time() - start_time
                if max_timeout and use_time > max_timeout:
                    # 超出最大超时时间
                    raise MaxTimeoutException(f"execute timeout, use time {use_time}s, max timeout {max_timeout}")

                try:
                    return await task_func(*args, **kwargs)
                except catch_exc as e:
                    print(f"fail {str(e)}")
                    await asyncio.sleep(time_interval)
            else:
                # 超过最大重试次数, 抛异常终止
                raise MaxRetryException(f"超过最大重试次数失败, max_retry_count {max_retry_count}")

        # 异步函数判断
        wrapper_func = async_wrapper if asyncio.iscoroutinefunction(task_func) else sync_wrapper
        return wrapper_func

    return _task_retry


@task_retry(max_retry_count=3, time_interval=1, catch_exc=ZeroDivisionError, max_timeout=5)
def user_place_order():
    a = 1 / 0
    print("user place order success")
    return {"code": 0, "msg": "ok"}


@task_retry(max_retry_count=5, time_interval=2, max_timeout=5)
async def user_place_order_async():
    """异步函数重试案例"""
    a = 1 / 0
    print("user place order success")
    return {"code": 0, "msg": "ok"}


async def io_test():
    """模拟io阻塞"""
    print("io test start")
    time.sleep(3)
    print("io test end")
    return "io test end"


async def main():
    # 同步案例
    try:
        ret = user_place_order()
        print(f"user place order ret {ret}")
    except MaxRetryException as e:
        # 超过最大重试次数处理
        print("MaxRetryException", e)
    except MaxTimeoutException as e:
        # 超过最大超时处理
        print("MaxTimeoutException", e)

    # 异步案例
    # ret = await user_place_order_async()
    # print(f"user place order ret {ret}")

    # 并发异步
    # order_ret, io_ret = await asyncio.gather(
    #     user_place_order_async(),
    #     io_test(),
    # )
    # print(f"io ret {io_ret}")
    # print(f"user place order ret {order_ret}")


if __name__ == '__main__':
    asyncio.run(main())
