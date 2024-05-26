import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from pathlib import Path
from apps import home, prediction_logreg
from plotly.io import templates

templates.default = "plotly"

st.set_page_config(
    page_title="Анализ просрочек у клиентов банка",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_and_process_data(client_path, credit_path, card_path, is_test=False):
    client_ds = pd.read_excel(client_path).drop_duplicates()
    credit_ds = pd.read_excel(credit_path).drop_duplicates()
    card_ds = pd.read_excel(card_path).drop_duplicates()

    # Объединение данных
    # Начнем с объединения client_ds с credit_ds и card_ds по CLIENT_ID
    df = pd.concat([
        pd.merge(client_ds, credit_ds, on='CLIENT_ID', how='right'),
        pd.merge(client_ds, card_ds, on='CLIENT_ID', how='right')
    ]).copy(deep=True)

    if not is_test:
        df['TARGET'] = df['OVERDUE_IND'].fillna(df['СС_OVERDUE_IND'])
    df['TERM']       = df['TERM'].str.replace('M', '', regex=False)
    df['VALUE_DT']   = pd.to_datetime(df['VALUE_DT'], format='%d.%m.%Y', errors='coerce')
    df['OPEN_DT']    = pd.to_datetime(df['OPEN_DT'], format='%d.%m.%Y', errors='coerce')

    # Извлечение года, месяца, дня и дня недели
    df['OPEN_DT_YEAR']      = df['VALUE_DT'].dt.year
    df['OPEN_DT_MONTH']     = df['VALUE_DT'].dt.month
    df['OPEN_DT_DAY']       = df['VALUE_DT'].dt.day
    df['OPEN_DT_DAYOFWEEK'] = df['VALUE_DT'].dt.dayofweek


    # Извлечение года, месяца, дня и дня недели
    df['VALUE_DT_YEAR']      = df['VALUE_DT'].dt.year
    df['VALUE_DT_MONTH']     = df['VALUE_DT'].dt.month
    df['VALUE_DT_DAY']       = df['VALUE_DT'].dt.day
    df['VALUE_DT_DAYOFWEEK'] = df['VALUE_DT'].dt.dayofweek

    # Заполнение пропущенных значений
    df.fillna({
        'CREDIT_TYPE'        : -1,
        'CREDIT_PURCHASE'    : 'None',
        'PRODUCT_CODE_x'     : 'None',
        'TERM'               : -1,
        'ORIG_AMOUNT'        : -1,
        'CURR_RATE_NVAL'     : -1,
        'VALUE_DT'           : '1900-01-01',
        'CARD_TYPE'          : 'None',
        'PRODUCT_CODE_y'     : 'None',
        'CС_LIMIT_NVAL'      : -1,
        'СС_GRACE_PERIOD'    : -1,
        'CURR_RATE'          : -1,
        'OPEN_DT'            : '1900-01-01',
        "OPEN_DT_YEAR"       : -1,
        "OPEN_DT_MONTH"      : -1,
        "OPEN_DT_DAY"        : -1,
        "OPEN_DT_DAYOFWEEK"  : -1,
        "VALUE_DT_YEAR"      : -1,
        "VALUE_DT_MONTH"     : -1,
        "VALUE_DT_DAY"       : -1,
        "VALUE_DT_DAYOFWEEK" : -1,
        'AGE'                : -1,
        'REGION'             : 'None',
        'GENDER'             : -1,
        'JOB'                : -1,
        'INCOME'             : -1,
        'MARITAL_STATUS'     : 'None',
        'IP_FLAG'            : -1,
        'SME_FLAG'           : -1,
        'EMPLOYEE_FLAG'      : -1,
        'REFUGEE_FLAG'       : -1,
        'PDN'                : -1

    }, inplace=True)

    df['TERM'] = df['TERM'].astype(int)
    df['AGE'] = df['AGE'].astype(int)

    # Удаление ненужных столбцов
    df = df.drop(['VALUE_DT', 'OPEN_DT', 'CLIENT_ID', 'ORGANIZATION', 'JOB', ], axis=1)
    if not is_test: df = df.drop(['OVERDUE_IND', 'СС_OVERDUE_IND'], axis=1)

    categorical_features = [
        'REGION', 'GENDER', 'MARITAL_STATUS', 'IP_FLAG', 'SME_FLAG', 'EMPLOYEE_FLAG',
        'REFUGEE_FLAG','CREDIT_TYPE', 'CREDIT_PURCHASE', 'PRODUCT_CODE', 'CARD_TYPE', 'TARGET'
    ]
    for column in categorical_features:
        df[column] = df[column].astype('category')
    return df


class Menu:
    apps = [
        {
            "func": home.app,
            "title": "Главная",
            "icon": "house-fill"
        },
        {
            "func": prediction_logreg.app,
            "title": "Прогнозирование",
            "icon": "person-check-fill"
        },
    ]

    def run(self):
        with st.sidebar:
            titles = [app["title"] for app in self.apps]
            icons = [app["icon"] for app in self.apps]

            st.sidebar.image(str(current_dir / 'images' / 'logo2.png'))
            
            selected = option_menu(
                "Меню",
                options=titles,
                icons=icons,
                menu_icon="cast",
                default_index=0,
            )
            st.info(
                """
                ## Анализ просрочек у клиентов банка
                Эта система анализа данных предназначена для банковского сектора с целью предсказания вероятности просрочек платежей по кредитам и кредитным картам. Она помогает в повышении эффективности управления рисками и улучшении клиентского обслуживания.
                """
            )
        return selected


if __name__ == '__main__':
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()

    # Загрузка и предварительная обработка данных
    client_path = current_dir / 'client_ds.xlsx'
    credit_path = current_dir / 'credit_ds.xlsx'
    card_path   = current_dir / 'card_ds.xlsx'
    df          = load_and_process_data(client_path, credit_path, card_path)

    menu = Menu()
    selected = menu.run()
    for app in menu.apps:
        if app["title"] == selected:
            app["func"](df, current_dir)
            break
