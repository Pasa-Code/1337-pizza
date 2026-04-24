import { h } from 'preact';
import { render, fireEvent, screen } from '@testing-library/preact';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ErrorDialogComponent from '../../components/ErrorDialogComponent';
import { AppStateContext } from '../../AppLogic';
import { ACTION_SERVER_ERROR_HANDLED } from '../../constants';
import { AppStateContextValue } from '../../types';
import { createAppState } from '../../flux/store/store';

// Mock context value
const mockPushAction = vi.fn();
const mockOnClose = vi.fn();
const contextValue : AppStateContextValue = {
  appState: createAppState(),
  executeAction: mockPushAction,
};

describe('ErrorDialogComponent', () => {
  beforeEach(() => {
    mockPushAction.mockClear();
    mockOnClose.mockClear();
  });

  function renderWithContext(props: any) {
    return render(
      <AppStateContext.Provider value={contextValue}>
        <ErrorDialogComponent {...props} />
      </AppStateContext.Provider>
    );
  }

  it('calls onClose when Escape is pressed', () => {
    renderWithContext({ error: 'Some error', isOpen: true, onClose: mockOnClose });
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(mockOnClose).not.toHaveBeenCalled();
    expect(mockPushAction).not.toHaveBeenCalled();
  });

  it('calls onClose and pushAction when Enter is pressed', () => {
    renderWithContext({ error: 'Some error', isOpen: true, onClose: mockOnClose });
    fireEvent.keyDown(document, { key: 'Enter' });
    expect(mockOnClose).toHaveBeenCalledTimes(1);
    expect(mockPushAction).toHaveBeenCalledWith({
      type: ACTION_SERVER_ERROR_HANDLED,
      payload: { error: 'Some error' },
    });
  });

  it('calls onClose and pushAction when acknowledge button is clicked (submit)', () => {
    renderWithContext({ error: 'Some error', isOpen: true, onClose: mockOnClose });
    const button = screen.getByRole('button', { name: /acknowledge/i });
    fireEvent.click(button);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
    expect(mockPushAction).toHaveBeenCalledWith({
      type: ACTION_SERVER_ERROR_HANDLED,
      payload: { error: 'Some error' },
    });
  });
});
