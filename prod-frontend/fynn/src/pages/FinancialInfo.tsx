import { useCallback, useState } from "react";
import { Button } from "@mui/material";
import Fynn100X100PxRectangle from "../components/Fynn100X100PxRectangle";
import FieldLabels from "../components/fieldLabels/FieldLabels";
import { useNavigate } from "react-router-dom";
import styles from "./FinancialInfo.module.css";
import fynnLogo from '../assets/fynn-100-x-100-px-rectangle-sticker-portrait-2@3x.png';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import { initializePlaid } from '../services/plaidService';

function FinancialInfo() {
  
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    income: "",
    assets: "",
    zipCode: ""
  });

  const incomeOptions = [
    "$0 - $12,000",
    "$12,001 - $50,000",
    "$50,001 - $100,000",
    "$100,001 - $200,000",
    "$200,001 - $250,000",
    "$250,001 - $600,000",
    "$600,000+"
  ];

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  const handleSubmit = () => {
    navigate("/goals");
    console.log(formData);
  };

  const handleSkip = () => {
    navigate("/goals");
  };

  const handlePlaidConnect = () => {
    initializePlaid().catch(console.error);
  };

  return (
    <div className={styles.financialInfo}>
      <Fynn100X100PxRectangle
        fynn100X100PxRectangleBackgroundImage={`url(${fynnLogo})`}
        showFynn
        fynnTextDecoration="none"
        fynnHeight="40px"
        fynnWidth="133px"
        fynnPosition="relative"
        fynnMargin="unset"
        fynnBottom="unset"
        fynnLeft="unset"
        fynnFontWeight="unset"
        fynnTop="unset"
      />
      <section className={styles.financialInfoWrapper}>
        <div className={styles.financialInfoPopUp}>
          <h1 className={styles.fynnFinancial}>Finances</h1>
          <form className={styles.frameGroup}>
            <div className={styles.inputArea}>
              <select 
                className={styles.selectInput}
                value={formData.income}
                onChange={(e) => setFormData({ ...formData, income: e.target.value })}
              >
                <option value="" disabled selected>Select Income Range</option>
                {incomeOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
              <FieldLabels 
                email="assets"
                placeholder="Enter your assets"
                fullWidth
                value={formData.assets}
                change={handleChange('assets')}
              />
              <FieldLabels
                email="zip code"
                placeholder="03062"
                fullWidth
                value={formData.zipCode}
                change={handleChange('zipCode')}
              />
            </div>
            <Button
              fullWidth
              variant="contained"
              sx={{
                background: "rgba(151, 229, 139, 0.77)",
                borderRadius: "20px",
                textTransform: "none",
                fontSize: "16px",
                padding: "8px 16px",
                "&:hover": { background: "rgba(151, 229, 139, 0.85)" },
              }}
              onClick={handleSubmit}
            >
              Continue
            </Button>
          </form>
          <div className={styles.disclaimer}>
            Disclaimer: The income data you provide is used solely to personalize your responses. 
            Your zip code is used to identify job opportunities and real estate options in your area. 
            We prioritize the security and confidentiality of your data.
          </div>
          <div className={styles.navigationButtons}>
            <div className={styles.skipButton} onClick={handleSkip}>
              <span>Skip</span>
              <ArrowBackIcon sx={{ fontSize: 20, marginLeft: '8px', transform: 'rotate(180deg)' }} />
            </div>
            <Button
              id="plaidButton"
              variant="contained"
              startIcon={<AccountBalanceIcon />}
              onClick={handlePlaidConnect}
              className={styles.plaidButton}
              sx={{
                background: "#9fdb95",
                color: "#000",
                textTransform: "none",
                fontSize: "16px",
                padding: "12px 24px",
                borderRadius: "8px",
                "&:hover": { background: "#8bc681" },
              }}
            >
              Connect to Plaid
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default FinancialInfo;
