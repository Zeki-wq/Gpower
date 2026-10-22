"""
G*Power Clone CLI Interface (gpower-clone)
"""

import sys
import json
import argparse
from typing import List, Optional
from src.calculator import (
    compute_a_priori,
    compute_post_hoc,
    ValidationError,
)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gpower-clone",
        description="G*Power İki Bağımsız Grup t-Testi Güç ve Örneklem Büyüklüğü Hesaplayıcı",
    )
    parser.add_argument(
        "--test",
        type=str,
        default="t2-indep",
        choices=["t2-indep"],
        help="İstatistiksel test türü (Varsayılan: t2-indep - İki bağımsız grup t-testi)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["a-priori", "post-hoc"],
        help="Analiz modu: 'a-priori' (örneklem hesabı) veya 'post-hoc' (güç hesabı)",
    )
    parser.add_argument(
        "--tails",
        type=int,
        default=2,
        choices=[1, 2],
        help="Kuyruk sayısı: 1 (tek kuyruk) veya 2 (çift kuyruk) (Varsayılan: 2)",
    )
    parser.add_argument(
        "--d",
        type=float,
        required=True,
        help="Cohen's d etki büyüklüğü (> 0)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Tip I hata olasılığı alfa (0 < alpha < 1) (Varsayılan: 0.05)",
    )
    # A priori parameters
    parser.add_argument(
        "--power",
        type=float,
        help="Hedef güç (1 - beta) (A priori için gereklidir, 0 < power < 1)",
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=1.0,
        help="Grup tahsis oranı N2/N1 (A priori için, Varsayılan: 1.0)",
    )
    # Post hoc parameters
    parser.add_argument(
        "--n1",
        type=int,
        help="Grup 1 örneklem büyüklüğü (Post hoc için gereklidir, n1 >= 2)",
    )
    parser.add_argument(
        "--n2",
        type=int,
        help="Grup 2 örneklem büyüklüğü (Post hoc için gereklidir, n2 >= 2)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="json",
        choices=["json", "text"],
        help="Çıktı formatı: 'json' veya 'text' (Varsayılan: json)",
    )
    return parser


def format_text_output(res: dict) -> str:
    lines = [
        "========================================",
        "  G*POWER CLONE - HESAPLAMA SONUÇLARI   ",
        "========================================",
        f"Test:                 {res.get('test')}",
        f"Mod:                  {res.get('mode')}",
        f"Kuyruk Sayısı:        {res.get('tails')}",
        f"Etki Büyüklüğü (d):   {res.get('d')}",
        f"Alfa (alpha):         {res.get('alpha')}",
    ]
    if res.get("mode") == "a-priori":
        lines.append(f"Hedef Güç (power):    {res.get('target_power')}")
        lines.append(f"Grup Oranı (N2/N1):   {res.get('ratio')}")
    lines.extend([
        "----------------------------------------",
        f"Grup 1 Örneklemi (N1): {res.get('n1')}",
        f"Grup 2 Örneklemi (N2): {res.get('n2')}",
        f"Toplam Örneklem (N):  {res.get('total_n')}",
        f"Serbestlik Derecesi:  {res.get('df')}",
        f"Noncentrality (delta):{res.get('delta'):.6f}",
        f"Kritik t:             {res.get('critical_t'):.6f}",
        f"Gerçekleşen Güç:      {res.get('actual_power'):.6f}",
        "========================================",
    ])
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = create_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # Argument parse error
        return e.code if isinstance(e.code, int) else 2

    try:
        if args.mode == "a-priori":
            if args.power is None:
                raise ValidationError("A priori analiz için '--power' parametresi zorunludur.")
            result = compute_a_priori(
                tails=args.tails,
                d=args.d,
                alpha=args.alpha,
                power=args.power,
                ratio=args.ratio,
            )
        elif args.mode == "post-hoc":
            if args.n1 is None or args.n2 is None:
                raise ValidationError("Post hoc analiz için '--n1' ve '--n2' parametreleri zorunludur.")
            result = compute_post_hoc(
                tails=args.tails,
                d=args.d,
                alpha=args.alpha,
                n1=args.n1,
                n2=args.n2,
            )
        else:
            raise ValidationError(f"Bilinmeyen mod: {args.mode}")

        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_text_output(result))

        return 0

    except ValidationError as ve:
        err_dict = {
            "status": "error",
            "error_type": "ValidationError",
            "message": str(ve),
        }
        print(json.dumps(err_dict, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1

    except Exception as ex:
        err_dict = {
            "status": "error",
            "error_type": type(ex).__name__,
            "message": str(ex),
        }
        print(json.dumps(err_dict, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
