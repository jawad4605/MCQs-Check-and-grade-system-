import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
samplefile1 = "data/sample1.xlsx"
samplefile2 = "data/sample2.xlsx"

default_difficulty_levels = (20,70)
default_discr_levels = (0.2, 0.4)

def get_key(df):
    return df.iloc[0, :]

def get_responses(df):
    return df.iloc[1:,:]

def load_data():
    if st.session_state.datasource=="sample":
        st.session_state.labels_in_first_row = True
        st.session_state.idx_first_col = True
        st.session_state.df = pd.read_excel(
            st.session_state.samplefile, 
            header=(0 if st.session_state.labels_in_first_row else None),
            index_col=(0 if st.session_state.idx_first_col else None)
            )
    elif st.session_state.datasource=="upload":
        if uploaded_file is None: # occurs when the uploaded file is removed
            st.stop() # wait until a file is chosen
        if uploaded_file.name.endswith("xlsx"):
            st.session_state.df = pd.read_excel(
                uploaded_file,
                header=(0 if st.session_state.labels_in_first_row else None),
                index_col=(0 if st.session_state.idx_first_col else None))
        if uploaded_file.name.endswith("csv"):
            uploaded_file.seek(0,0)
            st.session_state.df = pd.read_csv(
                uploaded_file, 
                header=(0 if st.session_state.labels_in_first_row else None),
                index_col=(0 if st.session_state.idx_first_col else False)
                )
    else:
        st.stop()

st.set_page_config(
    page_title="Test MMCQs Evaluation Tool",
    page_icon="img/icon.svg",
    layout="centered",
    initial_sidebar_state="expanded",
)
# Initial State
def initial_state():
    if 'df' not in st.session_state:
        st.session_state['df'] = None
    if 'datasource' not in st.session_state:
        st.session_state['datasource'] = None # None, "sample", or "upload"
    if 'labels_in_first_row' not in st.session_state:
        st.session_state["labels_in_first_row"] = False
    if "idx_first_col" not in st.session_state:
        st.session_state["idx_first_col"] = False

def reset_state():
    st.session_state['df'] = None
    st.session_state['datasource'] = None # None, "sample", or "upload"
    st.session_state["labels_in_first_row"] = False
    st.session_state["idx_first_col"] = False

initial_state()

st.image("img\MCQ Item Evaluation Tool.png", use_container_width=True)

"# Test MCQs Evaluation Tool"

with st.sidebar:
    "## About 👩🏻‍💻"
    "This application takes the responses of a multiple-choice test and calculates statistics of test items' difficulty and discriminative power."

    "## Demo 🕹️"
    "Click the button to load the sample response set and see its analysis results."
    def sample_click(samplefile):
        reset_state()
        st.session_state.datasource = "sample"
        st.session_state.samplefile = samplefile
    col1, col2 = st.columns(2)
    col1.button("Load Sample 1", on_click=sample_click, args=(samplefile1,))
    col2.button("Load Sample 2", on_click=sample_click, args=(samplefile2,))

    "## Upload your data 📂"
    "Single-sheet Excel or CSV file. Students in rows, items in columns. Solution key in the first row."
    def upload_change():
        reset_state()
        st.session_state.datasource = "upload"
    uploaded_file = st.file_uploader("Upload your data file", type=["xlsx","csv"], label_visibility="hidden", on_change=upload_change)
    
    "## Settings 🛠️"
    difficulty_hard, difficulty_medium = st.select_slider(
        "Set difficulty levels",
        options=range(5,100,5), # range limited to avoid error in pd.cut() below
        value=default_difficulty_levels)
    st.dataframe(
        pd.DataFrame(
            [f"0 to {difficulty_hard}", f"{difficulty_hard} to {difficulty_medium}", f"{difficulty_medium} to 100"],
            index=["Hard","Medium","Easy"]
            ).T,
            hide_index=True
    )
    disc_fair,disc_good = st.select_slider(
        "Set discrimination levels",
        options=[round(i/10,1) for i in range(1,10)], # range limited to avoid error in pd.cut() below
        value=default_discr_levels)
    st.dataframe(
        pd.DataFrame(
            [f"(-1.0) to {disc_fair}", f"{disc_fair} to {disc_good}", f"{disc_good} to 1.0"],
            index=["Poor","Fair","Good"]
            ).T,
            hide_index=True
    )
    
    st.divider()
    "Created and maintained by [Jawad Ahamd]"

report, help = st.tabs(["Report","Help"])

with help:
    with st.expander(label="Can I see a demonstration?"):
        """
        Click one of the "Load Sample" buttons in the sidebar to see the Test MMCQs Evaluation Tool in action, applied to a sample exam.
        """
    with st.expander(label="How should the input file be formatted?"):
        """
        The input file should have the responses arranged in rows. Every column corresponds to one response item (exam question).

        The first row can be used as column headings, and the first column can be used for labeling (e.g., student name, ID, etc.). If labels are omitted in data, the report will use automatically generated labels.

        The input table cannot have more than one row or column as labels. In other words, responses must begin either in the first or the second row, or in the first or second column.

        The solution key **must** be on the first row of responses (after column headings, if any).


        """
    with st.expander("What kind of responses are accepted? A-D, T/F,...?"):
        """
        Responses can be anything. The program does not care how the responses are labeled, 
        so it will work with {A,B,C,D}, or {T,F}, or {a,b,c,d,e}, or any mixture of them.

        However, "a" and "A" will be treated as different responses. If your data has both lowercase and uppercase responses, correct them before uploading.
        """
    with st.expander(label="Is my data secure?"):
        """
        This app does not store the data you upload, nor does it track its users. The data is discarded when you close the page.

        As an additional privacy measure, you can remove identifying columns from the data before uploading. The report will generate automatic labels.
        """
    with st.expander(label="What if my test has both multiple-choice and true-false questions?"):
        """
        The report handles such tests without problems. Each item will be evaluated separately according its own response set.
        You can have A-D responses, A-E responses, T/F responses, or any other discrete set of responses mixed in your test.
        """
    with st.expander(label="Can I analyze open-ended questions?"):
        """MCQ Item Evaluation Tool algorithms can work only with responses that are right or wrong. If you are not giving partial credit,
        you can encode the responses as T/F (or 1/0, or any other binary code as you please), and run the analysis on that."""

    with st.expander(label="How can I analyze different booklets of the same exam?"):
        """Some exams are given as different booklets where responses and/or items are randomly shuffled. 
        This app cannot analyze such exams directly.
        For such cases, we suggest you un-shuffle the responses and items, and combine them in a single table before uploading.
        """
    
    with st.expander(label="How is an item's difficulty calculated?"):
        """The difficulty of an item is defined as the fraction of correct answers, multiplied by 100."""
    
    with st.expander(label="How is an item's discrimination index calculated?"):
        """The discrimination index (DI) of an item can be defined in several different ways. Here we use a simple but useful form: 
        Count the correct answers to that item in the top 25% group and in the bottom 25% group, evaluated on the overall exam score.
        The DI is the difference between them, divided by the number of students in one of these groups."""
    
    with st.expander(label="How do you define easy, medium, and hard difficulty levels?"):
        f"""
        By default, "hard" is difficulty below {default_difficulty_levels[0]},"easy" is difficulty above {default_difficulty_levels[1]},
          and "medium" is between these values. These thresholds can be changed by adjusting the slider "Set difficulty levels" on the sidebar.
        """
    
    with st.expander(label="How do you define poor, fair, and good discrimination levels?"):
        f"""
        By default, if the discrimination index is below {default_discr_levels[0]} the item is said to have a poor discrimination,
        if it is above {default_discr_levels[1]} it has good discrimination, and values between these are fair (intermediate) discrimination.
        These thresholds can be changed by adjusting the slider "Set discrimination levels" on the sidebar.
        """


with report:
    #### Wait until the data is loaded
    if st.session_state.df is None:
        load_data()
            
    ##### ------  PREVIEW THE DATA SHEET -----
    st.write("## Data Preview 📄")
    st.write("*Check the correctness of your data. Edit and reupload if necessary.*")

    st.checkbox("Use first row as column labels", value=False, key="labels_in_first_row", on_change=load_data)
    st.checkbox("Use first column as index", value=False, key="idx_first_col", on_change=load_data)

    df = st.session_state.df.copy()
    
    if not st.session_state.labels_in_first_row:
        df.index.name = "ID"
        df.columns = [str(_) for _ in df.columns]

    if len(df.iloc[:,0].unique())==len(df.iloc[:,0]):
        st.error("First column appears to be an index. Try checking 'Use first column as index'",
                 icon="🚨")
    
    if len(df.iloc[0,:].unique())==len(df.iloc[0,:]):
        st.error("First row appears to contain column labels. Try checking 'Use first row as column labels'",
                 icon="🚨")
    
    key = get_key(df)
    responses = get_responses(df).replace([" ",pd.NA],"blank")
    st.dataframe(responses)
    grading = (responses==key) # table of boolean values showing correctness. NaN are possible.

    ##### -------- STUDENT SCORES -------

    st.write("## Student scores 👨‍🎓")
    """Scores and their statistics."""
    scores = grading.sum(axis=1)
    empty = responses.isna().sum(axis=1)
    incorrect = len(responses.columns) - scores - empty

    if all(scores==0):
        st.error("Possibly malformed data table. Try checking 'Use first row as column labels'",
                 icon="🚨")


    col1, col2 = st.columns([0.4,0.6])
    col1.dataframe(pd.DataFrame({"correct":scores,"incorrect":incorrect, "empty":empty}))
    col2.write(f"Mean score: {scores.mean():.2f}")
    col2.write(f"Score standard deviation: {scores.std():.2f}")
    fig = plt.figure()
    plt.hist(scores, bins=range(scores.min(), scores.max()+2), align="left",color="C0",rwidth=0.9)

    plt.title("Histogram")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    col2.write(fig)


    # Upper and lower quartile students
    sortedscores = scores.sort_values(ascending=False)
    n = len(scores)
    dfcomb = pd.merge(pd.DataFrame({"score":scores}), df, left_index=True, right_index=True)

    upper_quartile_idx = sortedscores[:(n//4)].index
    lower_quartile_idx = sortedscores[-(n//4):].index

    col1, col2 = st.columns(2)
    col1.write("Upper quartile students")
    col1.dataframe(dfcomb.loc[upper_quartile_idx])
    col2.write("Lower quartile students")
    col2.dataframe(dfcomb.loc[lower_quartile_idx])

    ##### --------- MCQ Item Evaluation Tool ----------
    st.write("## MCQ Item Evaluation Tool 🔬")
    difficulty = grading.mean(axis=0)*100
    discrimination_index = (grading.loc[upper_quartile_idx].sum() - grading.loc[lower_quartile_idx].sum()) / (len(upper_quartile_idx))

    difficulty_category = pd.cut(difficulty, bins=(0, difficulty_hard, difficulty_medium, 100), labels=("hard","medium","easy"))
    discrimination_category = pd.cut(discrimination_index, bins=(-1,disc_fair,disc_good,1), labels=("poor","fair","good"))
    itemdf = pd.DataFrame(
            {"key":key,
            "difficulty":difficulty.astype(int),
            "difficulty level":difficulty_category,
            "discrimination":discrimination_index.round(2),
            "discrimination level": discrimination_category,
            }
        )

    """The difficulty score (percentage of correct answers) and discrimination index for each item.
    """
    st.dataframe(itemdf)

    # Discrimination-difficulty matrix

    disc_diff = (
        itemdf
        .reset_index()
        [["index","difficulty level","discrimination level"]]
        .rename(columns={"index":"item"})
        .pivot_table(index="discrimination level", columns="difficulty level", aggfunc=lambda x:", ".join(x), observed=False)
        .stack(future_stack=True)
        .reindex(
            (
            ("poor","easy"),("poor","medium"),("poor","hard"),
            ("fair","easy"),("fair","medium"),("fair","hard"),
            ("good","easy"),("good","medium"),("good","hard")
            ))
        .unstack(sort=False)
        .fillna("-")
    )
    disc_diff.columns = disc_diff.columns.droplevel(0)

    """Items broken by difficulty level (easy, medium, hard) and discrimination level (poor, fair, good)."""
    st.table(disc_diff)

    ##### --------- DISTRACTOR ANALYSIS ----
    "## Distractor Analysis 📊"
    """*Frequency of every response for each item. Correct response shown in bold.*"""
    # generate a table of frequency of choices in each item
    choice_freqs = (
        pd.DataFrame(
            [c[1].value_counts().sort_index().to_dict() for c in responses.items()],
            index=responses.columns
            )
        .fillna(0)
        .astype(int)
    )
    # put blank count to the end of the table
    if "blank" in choice_freqs.columns:
        tmp = choice_freqs.columns.drop("blank")
        choice_freqs = choice_freqs[list(tmp)+["blank"]]

    styler = choice_freqs.style
    try:
        for k, v in key.items():
            styler.set_properties(**{"font-weight":"bold"}, subset=(k, v))
        st.table(styler)
    except KeyError:
        st.error("Possibly malformed data table. Try checking 'Use first row as column labels'",
                 icon="🚨")

    """
    *Response frequencies broken by upper and lower quartile groups*
    """
    responses_upq = responses.loc[upper_quartile_idx]
    responses_loq = responses.loc[lower_quartile_idx]
    plotcols = st.columns(3)

    for i,q in enumerate(responses.columns):
        resp = responses[q].value_counts().sort_index()
        ru = responses_upq[q].value_counts().sort_index()
        rl = responses_loq[q].value_counts().sort_index()
        cts = (
            pd.merge(rl, ru, how="outer", left_index=True, right_index=True)
            .set_axis(["lower 25%", "upper 25%"], axis=1)
            )
        fig = cts.plot(kind="bar", rot=0, figsize=(4,2), grid=True, xlabel="", title=f"Item {q}, key={key[q]}").figure
        fig.savefig("plotimg.png") # save as png for display
        plt.close(fig) # close figure to save memory
        plotcols[i%3].image("plotimg.png")

    