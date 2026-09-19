import shioaji as sj


def main():
    api = sj.Shioaji()

    print("Shioaji version:", sj.__version__)
    print()

    futures = api.Contracts.Futures

    print("=== Futures roots ===")
    print(futures)
    print()

    for root in ["TXF", "MXF", "TMF"]:
        print(f"=== {root} ===")

        try:
            contracts = getattr(futures, root)

            print("Root object:", contracts)
            print()

            # 嘗試列出合約
            for contract in contracts:
                print(
                    {
                        "code": getattr(contract, "code", None),
                        "symbol": getattr(contract, "symbol", None),
                        "name": getattr(contract, "name", None),
                        "category": getattr(contract, "category", None),
                        "delivery_month": getattr(contract, "delivery_month", None),
                        "delivery_date": getattr(contract, "delivery_date", None),
                        "last_trading_date": getattr(contract, "last_trading_date", None),
                        "begin_date": getattr(contract, "begin_date", None),
                        "end_date": getattr(contract, "end_date", None),
                        "multiplier": getattr(contract, "multiplier", None),
                        "tick": getattr(contract, "tick", None),
                        "limit_up": getattr(contract, "limit_up", None),
                        "limit_down": getattr(contract, "limit_down", None),
                    }
                )

        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")

        print()


if __name__ == "__main__":
    main()