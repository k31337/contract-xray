"""Unit tests for the rule/heuristic engine, using stub Slither objects."""

from contract_xray.rules.excessive_sell_tax import ExcessiveSellTaxRule
from contract_xray.rules.hidden_blacklist import HiddenBlacklistRule
from contract_xray.rules.unrenounced_ownership import UnrenouncedOwnershipRule
from contract_xray.rules.unrestricted_mint import UnrestrictedMintRule
from tests.conftest import StubContract, StubFunction, StubModifier, StubSlither, StubVariable


class TestUnrenouncedOwnershipRule:
    def test_flags_contract_with_owner_variable(self):
        contract = StubContract(name="Token", state_variables=[StubVariable(name="owner")])
        slither = StubSlither(contracts=[contract])

        findings = UnrenouncedOwnershipRule().evaluate(slither)

        assert len(findings) == 1
        assert findings[0].contract_name == "Token"
        assert findings[0].rule_id == "unrenounced-ownership"

    def test_flags_contract_with_transfer_ownership_function(self):
        contract = StubContract(name="Token", functions=[StubFunction(name="transferOwnership")])
        slither = StubSlither(contracts=[contract])

        findings = UnrenouncedOwnershipRule().evaluate(slither)

        assert len(findings) == 1

    def test_does_not_flag_contract_without_ownership_pattern(self):
        contract = StubContract(name="Token", state_variables=[StubVariable(name="totalSupply")])
        slither = StubSlither(contracts=[contract])

        findings = UnrenouncedOwnershipRule().evaluate(slither)

        assert findings == []


class TestHiddenBlacklistRule:
    def test_flags_contract_with_blacklist_mapping_and_setter(self):
        contract = StubContract(
            name="Token",
            state_variables=[StubVariable(name="isBlacklisted")],
            functions=[StubFunction(name="setBlacklist")],
        )
        slither = StubSlither(contracts=[contract])

        findings = HiddenBlacklistRule().evaluate(slither)

        assert len(findings) == 1
        assert "isBlacklisted" in findings[0].description

    def test_does_not_flag_contract_without_blacklist_state(self):
        contract = StubContract(name="Token", state_variables=[StubVariable(name="balances")])
        slither = StubSlither(contracts=[contract])

        findings = HiddenBlacklistRule().evaluate(slither)

        assert findings == []


class TestUnrestrictedMintRule:
    def test_flags_mint_function_without_access_control(self):
        contract = StubContract(name="Token", functions=[StubFunction(name="mint")])
        slither = StubSlither(contracts=[contract])

        findings = UnrestrictedMintRule().evaluate(slither)

        assert len(findings) == 1
        assert findings[0].rule_id == "unrestricted-mint"

    def test_does_not_flag_mint_function_with_access_control(self):
        contract = StubContract(
            name="Token",
            functions=[StubFunction(name="mint", modifiers=[StubModifier(name="onlyOwner")])],
        )
        slither = StubSlither(contracts=[contract])

        findings = UnrestrictedMintRule().evaluate(slither)

        assert findings == []

    def test_does_not_flag_view_functions(self):
        contract = StubContract(name="Token", functions=[StubFunction(name="mintedSupply", view=True)])
        slither = StubSlither(contracts=[contract])

        findings = UnrestrictedMintRule().evaluate(slither)

        assert findings == []


class TestExcessiveSellTaxRule:
    def test_flags_high_constant_tax(self):
        contract = StubContract(name="Token", state_variables=[StubVariable(name="sellTax", expression="30")])
        slither = StubSlither(contracts=[contract])

        findings = ExcessiveSellTaxRule().evaluate(slither)

        assert len(findings) == 1
        assert findings[0].rule_id == "excessive-sell-tax"

    def test_flags_adjustable_tax_setter(self):
        contract = StubContract(
            name="Token",
            state_variables=[StubVariable(name="sellTax", expression="5")],
            functions=[StubFunction(name="setSellTax")],
        )
        slither = StubSlither(contracts=[contract])

        findings = ExcessiveSellTaxRule().evaluate(slither)

        assert len(findings) == 1

    def test_does_not_flag_low_fixed_tax_without_setter(self):
        contract = StubContract(name="Token", state_variables=[StubVariable(name="sellTax", expression="5")])
        slither = StubSlither(contracts=[contract])

        findings = ExcessiveSellTaxRule().evaluate(slither)

        assert findings == []
