import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: '🚀 Easy Setup & Deploy',
    description: (
      <>
        Get anomaly detection running in minutes with Docker, GitHub Codespaces,
        Dagster Cloud, or local Python. No complex infrastructure required - just
        bring your metrics and we'll handle the ML.
      </>
    ),
  },
  {
    title: '🌟 Flexible Data Sources',
    description: (
      <>
        Connect to BigQuery, Snowflake, ClickHouse, DuckDB, SQLite, MotherDuck,
        Turso, and more. Define metrics with SQL or custom Python functions.
        Works with your existing data stack.
      </>
    ),
  },
  {
    title: '🧠 Intelligent Detection',
    description: (
      <>
        Powered by PyOD machine learning algorithms with configurable thresholds.
        Plus optional AI-powered anomaly detection using LLM agents for more
        nuanced analysis and explanations.
      </>
    ),
  },
  {
    title: '📧 Smart Alerts',
    description: (
      <>
        Get notified via Email and Slack with beautiful ASCII art plots and
        detailed context. Includes snoozing, feedback system, and daily summaries
        to reduce alert fatigue.
      </>
    ),
  },
  {
    title: '📊 Beautiful Dashboard',
    description: (
      <>
        Monitor your metrics with a modern FastHTML + MonsterUI dashboard.
        View trends, anomaly scores, feedback ratings, and manage alerts
        all in one place.
      </>
    ),
  },
  {
    title: '⚙️ Highly Configurable',
    description: (
      <>
        Customize everything from ML algorithms to alert routing with flexible
        YAML configs. Override settings per metric batch and add custom
        preprocessing functions.
      </>
    ),
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
