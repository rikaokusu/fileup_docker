# リストファイルの読み込み
import accounts.list.list_white



# 正規表現を作成する関数
def regcreate_white():
    subdomain_mae = "([\w]+@[\w]+?\.?("
    domain_mae = "([\w]+@("

    ato = "))"

    """任意の許可リスト読み込み"""
    white_domain = accounts.list.list_white.white_domain

    # リスト無いの文字列を結合させる
    white_domain_join =  '|'.join(white_domain)

    # ドメイン用とサブドメイン用の正規表現を生成
    domain_reg =  domain_mae + white_domain_join + ato
    subdomain_reg = subdomain_mae + white_domain_join + ato

    # 正規表現を生成
    reg = domain_reg + "|" + subdomain_reg

    return reg
