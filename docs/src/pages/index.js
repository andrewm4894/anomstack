import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro"
            style={{marginRight: '10px'}}>
            Get Started
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            href="https://anomstack-demo.replit.app/"
            target="_blank"
            style={{marginRight: '10px'}}>
            View Demo
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            href="https://github.com/andrewm4894/anomstack"
            target="_blank">
            GitHub
          </Link>
        </div>
      </div>
    </header>
  );
}

function DataSourcesSection() {
  return (
    <section className="padding-vert--lg">
      <div className="container">
        <div className="text--center">
          <Heading as="h2" className="margin-bottom--lg">
            Supported Data Sources & Platforms
          </Heading>
        </div>
        <div className="row">
          <div className="col col--6">
            <div className="card margin-bottom--md">
              <div className="card__header">
                <h3>🗄️ Data Sources</h3>
              </div>
              <div className="card__body">
                <div className="badge-container" style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
                  <span className="badge badge--primary">Python</span>
                  <span className="badge badge--primary">BigQuery</span>
                  <span className="badge badge--primary">Snowflake</span>
                  <span className="badge badge--primary">ClickHouse</span>
                  <span className="badge badge--primary">DuckDB</span>
                  <span className="badge badge--primary">SQLite</span>
                  <span className="badge badge--primary">MotherDuck</span>
                  <span className="badge badge--primary">Turso</span>
                  <span className="badge badge--warning">Redshift 🚧</span>
                </div>
              </div>
            </div>
          </div>
          <div className="col col--6">
            <div className="card margin-bottom--md">
              <div className="card__header">
                <h3>☁️ Model Storage</h3>
              </div>
              <div className="card__body">
                <div className="badge-container" style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
                  <span className="badge badge--success">Local</span>
                  <span className="badge badge--success">Google Cloud Storage</span>
                  <span className="badge badge--success">AWS S3</span>
                  <span className="badge badge--warning">Azure Blob 🚧</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function DeploymentSection() {
  return (
    <section className="padding-vert--lg" style={{backgroundColor: 'var(--ifm-color-emphasis-100)'}}>
      <div className="container">
        <div className="text--center margin-bottom--lg">
          <Heading as="h2">Deploy Anywhere</Heading>
          <p>Choose the deployment option that works best for you</p>
        </div>
        <div className="row">
          <div className="col col--2">
            <div className="card text--center">
              <div className="card__body">
                <h4>🐳 Docker</h4>
                <p>Self-hosted with Docker Compose</p>
              </div>
            </div>
          </div>
          <div className="col col--2">
            <div className="card text--center">
              <div className="card__body">
                <h4>☁️ Dagster Cloud</h4>
                <p>Serverless managed deployment</p>
              </div>
            </div>
          </div>
          <div className="col col--2">
            <div className="card text--center">
              <div className="card__body">
                <h4>🚀 Codespaces</h4>
                <p>GitHub cloud development</p>
              </div>
            </div>
          </div>
          <div className="col col--2">
            <div className="card text--center">
              <div className="card__body">
                <h4>🔧 Replit</h4>
                <p>Browser-based deployment</p>
              </div>
            </div>
          </div>
          <div className="col col--2">
            <div className="card text--center">
              <div className="card__body">
                <h4>🐍 Python Env</h4>
                <p>Local virtual environment</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className="padding-vert--xl">
      <div className="container">
        <div className="text--center">
          <Heading as="h2" className="margin-bottom--lg">
            Ready to detect anomalies in your metrics?
          </Heading>
          <p className="margin-bottom--lg" style={{fontSize: '1.2rem'}}>
            Join the growing community of developers using Anomstack for reliable, 
            open-source anomaly detection.
          </p>
          <div className={styles.buttons}>
            <Link
              className="button button--primary button--lg"
              to="/docs/quickstart"
              style={{marginRight: '15px'}}>
              Start with Quickstart
            </Link>
            <Link
              className="button button--outline button--primary button--lg"
              href="https://github.com/andrewm4894/anomstack/tree/main/metrics/examples"
              target="_blank">
              View Examples
            </Link>
          </div>
          <div style={{marginTop: '2rem'}}>
            <p style={{color: 'var(--ifm-color-emphasis-700)', fontSize: '0.9rem'}}>
              ⭐ Star us on GitHub if you find Anomstack useful!
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Open Source Anomaly Detection`}
      description="Painless open source anomaly detection for your metrics! Connect to BigQuery, Snowflake, ClickHouse, DuckDB and more. Deploy with Docker, Dagster Cloud, or GitHub Codespaces.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <DataSourcesSection />
        <DeploymentSection />
        <CTASection />
      </main>
    </Layout>
  );
}
