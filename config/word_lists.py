"""
Comprehensive word lists for ATS compliance checking.
Based on research-backed ATS optimization standards.
"""

# Approved Action Verbs (500+ verbs)
APPROVED_ACTION_VERBS = [
    'Explained', 'Farmed', 'Bred', 'Drafted', 'Traded', 'Unified', 'Sponsored', 'Retracted', 'Summarized', 'Uncoupled', 'Quartered', 'Served', 'Started', 'Conciliated', 'Raised', 'Defined', 'Portrayed', 'Merged', 'Collected', 'Reduced', 'Initiated', 'Troubleshooted', 'Executed', 'Visualized', 'Grew', 'Counseled', 'Upheld', 'Navigated', 'Overhauled', 'Rescinded', 'Sheltered', 'Designed', 'Converted', 'Perfected', 'Organized', 'Represented', 'Interviewed', 'Unplugged', 'Conserved', 'Supervised', 'Impelled', 'Bartered', 'Held', 'Stowed', 'Incited', 'Combined', 'Accommodated', 'Researched', 'Assessed', 'Published', 'Terminated', 'Reared', 'Overcame', 'Recommended', 'Improved', 'Audited', 'Repaired', 'Strengthened', 'Pitched', 'Traced', 'Lodged', 'Clarified', 'Restructured', 'Drove', 'Housed', 'Inspired', 'Taught', 'Enlisted', 'Closed', 'Piled', 'Shoved', 'Streamlined', 'Endorsed', 'Facilitated', 'Computed', 'Grouped', 'Curated', 'Participated', 'Standardized', 'Pioneered', 'Erased', 'Arranged', 'Fixed', 'Budgeted', 'Serviced', 'Bolstered', 'Deleted', 'Partnered', 'Ordered', 'Branded', 'Thrust', 'Patched', 'Detoxified', 'Spurred', 'Transcribed', 'Disinfected', 'Prioritized', 'Reigned', 'Lobbied', 'Reinstated', 'Protected', 'Appraised', 'Mentored', 'Reimbursed', 'Pushed', 'Stored', 'Joined', 'Positioned', 'Assisted', 'Equipped', 'Spearheaded', 'Repaid', 'Optimized', 'Lectured', 'Cultivated', 'Fed', 'Decontaminated', 'Exhibited', 'Approved', 'Offset', 'Segregated', 'Shielded', 'Campaigned', 'Neutralized', 'Expanded', 'Enabled', 'Commanded', 'Led', 'Automated', 'Nurtured', 'Allocated', 'Persuaded', 'Authored', 'Buttressed', 'Advocated', 'Modernized', 'Attained', 'Scaled', 'Restored', 'Accompanyied', 'Planned', 'Supported', 'Bargained', 'Managed', 'Resolved', 'Boosted', 'Advanced', 'Provisioned', 'Invalidated', 'Kept', 'Monitored', 'Classified', 'Verified', 'Ushered', 'Illustrated', 'Reaped', 'Balanced', 'Structured', 'Maintained', 'Achieved', 'Aided', 'Gathered', 'Instituted', 'Revoked', 'Recalled', 'Sifted', 'Urged', 'Swapped', 'Produced', 'Proofread', 'Cataloged', 'Co-authored', 'Escorted', 'Synthesized', 'Purified', 'Chaired', 'Founded', 'Forecasted', 'Reviewed', 'Indexed', 'Instigated', 'Teamed', 'Guarded', 'Addressed', 'Refined', 'Educated', 'Prepared', 'Dominated', 'Administered', 'Predicted', 'Abstracted', 'Established', 'Refurbished', 'Arbitrated', 'Counteracted', 'Retained', 'Harvested', 'Accumulated', 'Adapted', 'Disassociated', 'Conceived', 'Filtered', 'Archived', 'Armed', 'Renovated', 'Heaped', 'Cancelled', 'Demonstrated', 'Attended', 'Reshuffled', 'Liquidated', 'Reorganized', 'Liaised', 'Stimulated', 'Maximized', 'Sanitized', 'Returned', 'Reconstituted', 'Instructed', 'Surveyed', 'Divested', 'Unlinked', 'Withdrew', 'Counselled', 'Volunteered', 'Slashed', 'Reinforced', 'Exchanged', 'Lowered', 'Distanced', 'Identified', 'Oversaw', 'Scheduled', 'Extracted', 'Acquired', 'Mended', 'Rebuilt', 'Originated', 'Coordinated', 'Marshaled', 'Marketed', 'Purged', 'Fostered', 'Recorded', 'Steered', 'Saved', 'Presented', 'Propelled', 'Inspected', 'Tripled', 'Hired', 'Substituted', 'Officiated', 'Settled', 'Purchased', 'Corresponded', 'Launched', 'Conceptualized', 'Collated', 'Harbored', 'Migrated', 'Coded', 'Extrapolated', 'Promoted', 'Transformed', 'Haggled', 'Expedited', 'Validated', 'Translated', 'Removed', 'Mastered', 'Defended', 'Detached', 'Advised', 'Mediated', 'Trained', 'Emboldened', 'Released', 'Reconstructed', 'Informed', 'Tested', 'Revised', 'Chaperoned', 'Clustered', 'Revitalized', 'Moderated', 'Composed', 'Accelerated', 'Developed', 'Expunged', 'Boarded', 'Furthered', 'Motivated', 'Investigated', 'Partitioned', 'Conducted', 'Replaced', 'Assigned', 'Broadened', 'Goaded', 'Refactored', 'Depicted', 'Awarded', 'Annulled', 'Systemized', 'Discovered', 'Negotiated', 'Amassed', 'Controlled', 'Nullified', 'Sustained', 'Donated', 'Debugged', 'Uncovered', 'Coached', 'Opened', 'Screened', 'Cleansed', 'Updated', 'Evaluated', 'Advertised', 'Assembled', 'Performed', 'Catalogued', 'Critiqued', 'Pruned', 'Compensated', 'Gleaned', 'Implemented', 'Systematized', 'Configured', 'Devised', 'Segmented', 'Helped', 'Split', 'Eliminated', 'Modeled', 'Doubled', 'Remodeled', 'Invented', 'Consolidated', 'Sterilized', 'Dealt', 'Customized', 'Decreed', 'Widened', 'Completed', 'Created', 'Hoarded', 'Demoed', 'Provoked', 'Fashioned', 'Redesigned', 'Deployed', 'Influenced', 'Owned', 'Shaped', 'Proposed', 'Sold', 'Convinced', 'Reordered', 'Divided', 'Categorized', 'Disconnected', 'Voided', 'Fortified', 'Upgraded', 'Minimised', 'Delegated', 'Increased', 'Engineered', 'Fundraised', 'Contracted', 'Trimmed', 'Stacked', 'Shepherded', 'Onboarded', 'Refunded', 'Retrieved', 'Separated', 'Backed', 'Negated', 'Piloted', 'Analyzed', 'Estimated', 'Dispatched', 'Recruited', 'Processed', 'Cut', 'Projected', 'Prescribed', 'Possessed', 'Presided', 'Collaborated', 'Formulated', 'Compiled', 'Solved', 'Preserved', 'Transacted', 'Diagnosed', 'Reconciled', 'Generated', 'Operated', 'Orchestrated', 'Interpreted', 'Simplified', 'Introduced', 'Polished', 'Minimized', 'Bankrupted', 'Effected', 'Examined', 'Contributed', 'Communicated', 'Integrated', 'Billeted', 'Documented', 'Directed', 'Specified', 'Edited', 'Revamped', 'Mandated', 'Governed', 'Isolated', 'Decreased', 'Enhanced', 'Wrote', 'Encouraged', 'Rearranged', 'Dictated', 'Headed', 'Nourished', 'Installed', 'Cooperated', 'Ruled', 'Calculated', 'Innovated', 'Guided', 'Empowered', 'Showcased', 'Publicized', 'Architected', 'Sorted'
]

# Banned Terms (200+ jargon/buzzwords)
BANNED_TERMS = [
    'Ambitious', 'Problem Solving', 'Strong technical skills', 'Strong presentation skills', 'Strong leadership skills', 'Innovative thinker', 'Strong interpersonal skills', 'Creative strategist', 'Unique thinker', 'Well-rounded', 'Detail-oriented', 'Professional thinker', 'Strong analytical skills', 'Strong initiative', 'Strong business acumen', 'Strong problem-solving ability', 'Strong coaching skills', 'Strong relationship builder', 'Strong collaborator', 'Strong communication skills', 'Good interpersonal skills', 'Excellent written and verbal communication skills', 'Excellent communicator', 'Effective communicator', 'Exceptional communicator', 'Motivated leader', 'Enthusiastic professional', 'People-oriented', 'Growth-driven', 'Business-minded', 'Forward-looking', 'Positive attitude', 'Motivational', 'Resilient', 'Flexible', 'Adaptable', 'Committed', 'Enthusiastic', 'High performer', 'Driven', 'Trustworthy', 'Reliable', 'Dependable', 'Energetic', 'Visionary', 'Seasoned', 'Dedicated', 'Successful', 'Hard-working', 'Passionate', 'Dynamic', 'Go-getter', 'Self-starter', 'Motivated', 'Results-driven', 'Leadership qualities', 'Proven leadership', 'Demonstrated leadership', 'Accomplished leader', 'Committed leader', 'Effective leader', 'Adaptive leader', 'Distinguished professional', 'Recognized leader', 'Inspiring leader', 'Transformational', 'Strategic partner', 'Strategic thinker', 'Strategic implementer', 'Strategic asset', 'Business leader', 'Senior professional', 'Trusted advisor', 'Recognized authority', 'Subject matter expert', 'Go-to person', 'Go-to expert', 'Key contributor', 'Benchmark setter', 'Industry leader', 'Visionary professional', 'Trailblazer', 'Thought leader', 'Change agent', 'Recognized expert', 'Synergy', 'Leverage', 'Think outside the box', 'Out-of-the-box thinker', 'Game-changer', 'Paradigm shift', 'Best-in-class', 'Best practices', 'Mission-critical', 'Value-added', 'KPI-driven', 'Impactful', 'Action-oriented', 'Move the needle', 'Core competency', 'Cutting-edge', 'Groundbreaking', 'Next-gen', 'Leading-edge', 'Robust', 'Scalable', 'Disruptive', 'Pioneering', 'Forward-thinking', 'Hands-on', 'High-impact', 'Growth hacker', 'Professional excellence', 'Operational excellence', 'High-value', 'Business-savvy', 'Cutting-edge innovator', 'Strategic', 'Tactical', 'Tactical executor', 'Forward-leaning', 'Team player', 'People person', 'Collaborative mindset', 'Persuasive', 'Influential', 'Strong influencer', 'Fast learner', 'Quick learner', 'Multi-tasker', 'Detail-focused', 'Customer-focused', 'Client-centric', 'Analytical thinker', 'Critical thinker', 'Creative problem solver', 'Solution-oriented', 'Innovative leader', 'Adept problem-solver', 'Superior skills', 'Adept', 'Distinctive skills', 'Cross-functional expertise', 'Strong organizational skills', 'High-level thinker', 'Big-picture thinker', 'Responsible for', 'Tasked with', 'Duties included', 'Assisted with', 'Helped with', 'Worked on', 'Handled', 'Proven track record', 'Proven ability', 'Proven success', 'Proven performer', 'Proven results', 'Proven potential', 'Proven expertise', 'Demonstrated expertise', 'Demonstrated success', 'Demonstrated impact', 'Achieved excellence', 'Outstanding track record', 'Outstanding professional', 'Outstanding abilities', 'Outstanding performance', 'Distinguished career', 'Exceptional skills', 'Exceptional', 'Top performer', 'Top talent', 'Top-caliber', 'Top achiever', 'High achiever', 'Overachiever', 'Above and beyond', 'Over-delivered', 'Well-respected', 'Recognized performer', 'Recognized professional', 'Award-winning', 'Industry pioneer', 'Successful professional', 'Standout professional', 'Innovative', 'Creative', 'Rockstar', 'Ninja', 'Guru', 'Wizard', 'Jedi', 'Unicorn', 'Sherpa', 'Evangelist', 'Hacker', 'Code monkey', 'Grunt', 'Minion', 'Cog', 'Drone', 'Resource', 'Headcount', 'FTE', 'Bandwidth', 'Cycle time', 'Face time', 'Low-hanging fruit', 'Deep dive', 'Circle back', 'Touch base', 'Offline', 'Blue sky', 'Boil the ocean', 'Deliverable', 'Ecosystem', 'Empowerment', 'Holistic', 'Ideation', 'Incentivize', 'Mindshare', 'Paradigm', 'Proactive', 'Value-add', 'Vertical', 'Win-win', 'Wheelhouse'
]

# Global Stopwords (150+ words)
STOPWORDS = [
    'a', 'an', 'the', 'this', 'that', 'these', 'those', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'own', 'same', 'and', 'or', 'but', 'if', 'then', 'else', 'than', 'because', 'as', 'until', 'while', 'nor', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'whose', 'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would', 'do', 'does', 'did', 'doing', 'done', 'have', 'has', 'had', 'having', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'again', 'further', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'not', 'only', 'so', 'too', 'very', 'just', 'now', 'ever', 'never', 'much', 'many', 'least', 'less', 'rather', 'quite', 'even', 'hence', 'thus', 'therefore', 'thereby', 'hereby', 'wherein', 'whereby', 'wherefore', 'whither', 'hither', 'thither', 'whence', 'thence', 'henceforth', 'hereafter', 'thereafter', 'whereas', 'notwithstanding', 'nevertheless', 'nonetheless', 'furthermore', 'moreover', 'however', 'although', 'though', 'albeit', 'meanwhile', 'meantime', 'otherwise'
]

# Common contractions mapping (for expansion before stopword check)
CONTRACTIONS_MAP = {
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "can't": "can not",
    "couldn't": "could not",
    "won't": "will not",
    "wouldn't": "would not",
    "shouldn't": "should not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "haven't": "have not",
    "hasn't": "has not",
    "hadn't": "had not",
    "I'm": "I am",
    "you're": "you are",
    "he's": "he is",
    "she's": "she is",
    "it's": "it is",
    "we're": "we are",
    "they're": "they are",
    "I've": "I have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "I'd": "I would",
    "you'd": "you would",
    "he'd": "he would",
    "she'd": "she would",
    "we'd": "we would",
    "they'd": "they would",
    "I'll": "I will",
    "you'll": "you will",
    "he'll": "he will",
    "she'll": "she will",
    "we'll": "we will",
    "they'll": "they will"
}

# Metric/quantification patterns (regex-compatible)
METRIC_PATTERNS = [
    r'\d+%',           # 25%
    r'\d+\+',          # 10+
    r'\$\d+[KMB]?',    # $50K, $2M
    r'\d+x',           # 3x
    r'\d+[KMB]',       # 50K, 2M
    r'\d+\.\d+',       # 3.5
    r'\d+',            # Simple numbers
]
